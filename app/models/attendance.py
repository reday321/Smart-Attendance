from datetime import datetime, timedelta
from .. import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    classroom = db.Column(db.String(50))
    week_schedule = db.Column(db.String(100))  # e.g., "Monday,Wednesday,Friday"
    students = db.relationship('CourseEnrollment', backref='course', lazy=True)
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('courses_taught', lazy=True))

class CourseEnrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    student = db.relationship('User', foreign_keys=[student_id], backref=db.backref('enrollments', lazy=True))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow())
    status = db.Column(db.String(20), nullable=False, default='present')  # present, absent, late
    timezone_offset = db.Column(db.Integer, default=6)  # UTC+6 for Bangladesh

    @property
    def local_time(self):
        """Return the attendance time in local timezone (Bangladesh)"""
        return self.date + timedelta(hours=self.timezone_offset)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'pending', 'rejected'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    student = db.relationship('User', foreign_keys=[student_id])
    course = db.relationship('Course', foreign_keys=[course_id])