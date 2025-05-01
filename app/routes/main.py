from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models.attendance import Course, CourseEnrollment, Attendance
from ..models.user import User
from .. import db
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    if current_user.role == 'student':
        # Get enrollments and available courses
        enrollments = CourseEnrollment.query.filter_by(
            student_id=current_user.id,
            status='approved'
        ).all()
        
        available_courses = Course.query.filter(
            ~Course.id.in_(
                db.session.query(CourseEnrollment.course_id)
                .filter_by(student_id=current_user.id)
            )
        ).all()

        # Calculate attendance statistics
        course_names = []
        course_attendance = []
        total_attended = 0
        total_classes = 0

        # Calculate course-wise attendance
        for enrollment in enrollments:
            course_names.append(enrollment.course.name)
            
            attended = Attendance.query.filter_by(
                student_id=current_user.id,
                course_id=enrollment.course.id,
                status='present'
            ).count()
            
            total = Attendance.query.filter_by(
                student_id=current_user.id,
                course_id=enrollment.course.id
            ).count()
            
            attendance_percentage = round((attended / total * 100) if total > 0 else 0)
            course_attendance.append(attendance_percentage)
            
            total_attended += attended
            total_classes += total
            
            # Add attendance percentage to enrollment object for the template
            enrollment.attendance_percentage = attendance_percentage

        # Calculate overall attendance percentage
        overall_attendance = round((total_attended / total_classes * 100) if total_classes > 0 else 0)
        enrolled_courses = len(enrollments)

        return render_template('main/student_dashboard.html',
                             enrollments=enrollments,
                             available_courses=available_courses,
                             course_names=course_names,
                             course_attendance=course_attendance,
                             overall_attendance=overall_attendance,
                             total_classes=total_classes,
                             enrolled_courses=enrolled_courses,
                             timedelta=timedelta)

    elif current_user.role == 'teacher':
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        return render_template('main/teacher_dashboard.html', 
                             courses=courses,
                             timedelta=timedelta)
    
    else:  # admin
        courses = Course.query.all()
        users = User.query.all()

        # Get attendance statistics in Bangladesh time
        today = datetime.utcnow() + timedelta(hours=6)
        stats = {
            'total_present': Attendance.query.filter_by(status='present').count(),
            'total_absent': Attendance.query.filter_by(status='absent').count(),
            'today_present': Attendance.query.filter(
                Attendance.status == 'present',
                func.date(Attendance.date + timedelta(hours=6)) == today.date()
            ).count(),
            'today_absent': Attendance.query.filter(
                Attendance.status == 'absent',
                func.date(Attendance.date + timedelta(hours=6)) == today.date()
            ).count()
        }
        
        return render_template('main/admin_dashboard.html', 
                             courses=courses, 
                             users=users,
                             stats=stats,
                             timedelta=timedelta)

@bp.route('/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'teacher':
        flash('Only teachers can create courses')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Get selected days from week_schedule checkboxes
        week_schedule = request.form.getlist('week_schedule')
        week_schedule_str = ','.join(week_schedule)  # Convert list to comma-separated string
        
        course = Course(
            name=request.form['name'],
            department=request.form['department'],
            classroom=request.form['classroom'],
            week_schedule=week_schedule_str,
            teacher_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully')
        return redirect(url_for('main.index'))
    
    return render_template('main/create_course.html')

@bp.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    if current_user.role != 'student':
        flash('Only students can enroll in courses')
        return redirect(url_for('main.index'))
    
    enrollment = CourseEnrollment(
        course_id=course_id,
        student_id=current_user.id,
        status='pending'
    )
    db.session.add(enrollment)
    db.session.commit()
    flash('Enrollment request sent')
    return redirect(url_for('main.index'))

@bp.route('/enrollment/<int:enrollment_id>/<action>')
@login_required
def manage_enrollment(enrollment_id, action):
    if current_user.role != 'teacher':
        flash('Only teachers can manage enrollments')
        return redirect(url_for('main.index'))
    
    enrollment = CourseEnrollment.query.get_or_404(enrollment_id)
    course = Course.query.get(enrollment.course_id)
    
    if course.teacher_id != current_user.id:
        flash('You can only manage enrollments for your own courses')
        return redirect(url_for('main.index'))
    
    if action == 'approve':
        enrollment.status = 'approved'
        flash('Enrollment approved')
    elif action == 'reject':
        enrollment.status = 'rejected'
        flash('Enrollment rejected')
    
    db.session.commit()
    return redirect(url_for('main.index'))