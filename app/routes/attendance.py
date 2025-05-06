from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
import face_recognition
import cv2
import numpy as np
from .. import db
from ..models.user import User
from ..models.attendance import Course, CourseEnrollment, Attendance
import os
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@bp.route('/register-face', methods=['GET', 'POST'])
@login_required
def register_face():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        image = face_recognition.load_image_file(file)
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            return jsonify({'error': 'No face detected'}), 400
            
        face_encoding = face_recognition.face_encodings(image, face_locations)[0]
        current_user.face_encoding = face_encoding.tolist()
        db.session.commit()
        
        return jsonify({'message': 'Face registered successfully'})
    
    return render_template('attendance/register_face.html')

@bp.route('/mark/<int:course_id>', methods=['GET', 'POST'])
@login_required
def mark_attendance(course_id):
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        file = request.files['image']
        image = face_recognition.load_image_file(file)
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            return jsonify({'error': 'No face detected'}), 400
            
        face_encoding = face_recognition.face_encodings(image, face_locations)[0]
        
        if not current_user.face_encoding:
            return jsonify({'error': 'Please register your face first'}), 400
            
        stored_encoding = np.array(current_user.face_encoding)
        
        # Calculate face distance and confidence
        face_distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
        confidence = 1 - face_distance  # Convert distance to confidence (0 to 1)
        confidence_percentage = confidence * 100
        
        # Check if faces match with at least 70% confidence
        if confidence_percentage >= 70:
            # Get current time in Bangladesh time then convert to UTC for storage
            bd_time = datetime.utcnow() + timedelta(hours=6)
            utc_time = bd_time - timedelta(hours=6)
            
            # Record attendance
            attendance = Attendance(
                student_id=current_user.id,
                course_id=course_id,
                date=utc_time,
                status='present'
            )
            db.session.add(attendance)
            db.session.commit()
            
            return jsonify({
                'message': 'Attendance marked successfully',
                'confidence': f'{confidence_percentage:.2f}%'
            })
        else:
            return jsonify({
                'error': 'Face verification failed',
                'confidence': f'{confidence_percentage:.2f}%'
            }), 400
        
    return render_template('attendance/mark_attendance.html', course_id=course_id)

@bp.route('/report/<int:course_id>')
@login_required
def attendance_report(course_id):
    if current_user.role == 'teacher':
        course = Course.query.filter_by(id=course_id, teacher_id=current_user.id).first_or_404()
        enrollments = CourseEnrollment.query.filter_by(course_id=course_id, status='approved').all()
        attendance_data = []
        
        for enrollment in enrollments:
            student = User.query.get(enrollment.student_id)
            attendance_records = Attendance.query.filter_by(
                student_id=student.id,
                course_id=course_id
            ).order_by(Attendance.date.desc()).all()
            
            attendance_data.append({
                'student': student,
                'records': attendance_records
            })
            
        return render_template('attendance/report.html', 
                             course=course, 
                             attendance_data=attendance_data,
                             timedelta=timedelta)  # Pass timedelta to template
    else:
        flash('Only teachers can view attendance reports', 'error')
        return redirect(url_for('main.index'))