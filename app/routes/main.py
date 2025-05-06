from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models.attendance import Course, CourseEnrollment, Attendance, Notification
from ..models.user import User
from .. import db
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    if current_user.role == 'student':
        # Get unread notifications
        notifications = Notification.query.filter_by(
            student_id=current_user.id,
            is_read=False
        ).order_by(Notification.created_at.desc()).all()
        
        # Get enrollments for available courses section
        enrollments = CourseEnrollment.query.filter_by(
            student_id=current_user.id
        ).all()
        
        # Get available courses (now including rejected ones)
        available_courses = Course.query.filter(
            ~Course.id.in_(
                db.session.query(CourseEnrollment.course_id)
                .filter_by(student_id=current_user.id, status='pending')
                .union(
                    db.session.query(CourseEnrollment.course_id)
                    .filter_by(student_id=current_user.id, status='approved')
                )
            )
        ).all()

        # Calculate attendance statistics
        course_names = []
        course_attendance = []
        total_attended = 0
        total_classes = 0

        # Calculate course-wise attendance for approved enrollments only
        for enrollment in enrollments:
            if enrollment.status == 'approved':
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
            else:
                # Set attendance percentage to 0 for non-approved enrollments
                enrollment.attendance_percentage = 0

        # Calculate overall attendance percentage (only for approved courses)
        overall_attendance = round((total_attended / total_classes * 100) if total_classes > 0 else 0)
        enrolled_courses = len([e for e in enrollments if e.status == 'approved'])

        return render_template('main/student_dashboard.html',
                             enrollments=enrollments,
                             notifications=notifications,
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

    # Create pending notification
    notification = Notification(
        student_id=current_user.id,
        course_id=course_id,
        message=f'Your enrollment request for {Course.query.get(course_id).name} is pending teacher approval.',
        type='pending'
    )
    db.session.add(notification)
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
        # Delete any pending notifications
        Notification.query.filter_by(
            student_id=enrollment.student_id,
            course_id=enrollment.course_id,
            type='pending'
        ).delete()
        flash('Enrollment approved')
    elif action == 'reject':
        # Delete pending notification and create rejection notification
        Notification.query.filter_by(
            student_id=enrollment.student_id,
            course_id=enrollment.course_id,
            type='pending'
        ).delete()
        
        notification = Notification(
            student_id=enrollment.student_id,
            course_id=enrollment.course_id,
            message=f'Your enrollment request for {course.name} was not approved. You can request enrollment again.',
            type='rejected'
        )
        db.session.add(notification)
        # Delete the rejected enrollment so the course becomes available again
        db.session.delete(enrollment)
        flash('Enrollment rejected')
    
    db.session.commit()
    return redirect(url_for('main.index'))

@bp.route('/notification/<int:notification_id>/dismiss', methods=['POST'])
@login_required
def dismiss_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.index'))
    
    students = User.query.filter_by(role='student').all()
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('main/admin_users.html', students=students, teachers=teachers)

@bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete admin users')
        return redirect(url_for('main.manage_users'))
    
    try:
        # Delete all notifications related to the user
        Notification.query.filter_by(student_id=user.id).delete()
        
        # Delete all attendance records
        Attendance.query.filter_by(student_id=user.id).delete()
        
        # Delete all course enrollments
        CourseEnrollment.query.filter_by(student_id=user.id).delete()
        
        # If user is a teacher, reassign or delete their courses
        if user.role == 'teacher':
            # Delete all courses taught by this teacher
            Course.query.filter_by(teacher_id=user.id).delete()
        
        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been deleted')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user. Please try again.')
        
    return redirect(url_for('main.manage_users'))

@bp.route('/admin/course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def manage_course(course_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        course.name = request.form['name']
        course.department = request.form['department']
        course.classroom = request.form['classroom']
        course.teacher_id = int(request.form['teacher_id'])
        db.session.commit()
        flash('Course updated successfully')
        return redirect(url_for('main.index'))
    
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('main/admin_edit_course.html', course=course, teachers=teachers)

@bp.route('/admin/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.index'))
    
    try:
        course = Course.query.get_or_404(course_id)
        
        # Delete all notifications related to this course
        Notification.query.filter_by(course_id=course_id).delete()
        
        # Delete all attendance records for this course
        Attendance.query.filter_by(course_id=course_id).delete()
        
        # Delete all enrollments for this course
        CourseEnrollment.query.filter_by(course_id=course_id).delete()
        
        # Finally delete the course
        db.session.delete(course)
        db.session.commit()
        flash(f'Course {course.name} has been deleted')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting course. Please try again.')
        
    return redirect(url_for('main.index'))