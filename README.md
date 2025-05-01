# Smart Attendance System with Face Recognition

A web-based attendance management system that uses face recognition technology to automate attendance tracking for educational institutions.

## Features

- User Authentication (Students, Teachers, Admins)
- Face Registration for Students
- Automated Attendance Marking using Face Recognition
- Course Management
- Real-time Attendance Reports
- Student Enrollment System
- Role-based Access Control
- Secure Face Encoding Storage

## Prerequisites

- Python 3.10 or higher
- Webcam access for face recognition
- Sufficient storage for face encodings
- Windows/Linux/MacOS supported

## Technologies Used

- Backend: Python Flask 3.0.0
- Database: SQLite with SQLAlchemy 3.1.1
- Frontend: HTML, Bootstrap 5
- Face Recognition: OpenCV 4.5.5, face-recognition 1.3.0
- Authentication: Flask-Login 0.6.2
- Image Processing: Pillow 10.0.0, NumPy 1.24.3

## Setup Instructions

1. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python reset_db.py
```

4. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## User Roles

### Student
- Register and login
- Register face for attendance
- View available courses
- Request course enrollment
- Mark attendance using face recognition
- View attendance history

### Teacher
- Create and manage courses
- Approve/reject student enrollments
- View attendance reports
- Monitor student attendance

### Admin
- Manage all users and courses
- View system-wide reports
- Monitor attendance across all courses
- System configuration management

## Project Structure

```
.
├── app/
│   ├── models/          # Database models
│   │   ├── user.py     # User model definitions
│   │   └── attendance.py# Attendance records
│   ├── routes/          # Route handlers
│   │   ├── auth.py     # Authentication routes
│   │   ├── main.py     # Main application routes
│   │   └── attendance.py# Attendance management
│   ├── static/          # Static files (CSS, images)
│   └── templates/       # HTML templates
├── instance/            # Database instance
├── requirements.txt     # Project dependencies
├── reset_db.py         # Database initialization
└── run.py              # Application entry point
```

## API Endpoints

### Authentication
- `/login` - User login
- `/register` - User registration
- `/logout` - User logout
- `/profile` - User profile management

### Attendance
- `/attendance/register-face` - Register student face
- `/attendance/mark/<course_id>` - Mark attendance
- `/attendance/report/<course_id>` - View attendance report

### Course Management
- `/course/create` - Create new course
- `/course/<course_id>/enroll` - Enroll in course
- `/enrollment/<enrollment_id>/<action>` - Manage enrollment requests

## Security Considerations

- Face encodings are stored securely in the database
- Password hashing using Werkzeug security
- Role-based access control
- Session management with Flask-Login
- Input validation and sanitization
- CSRF protection enabled

## Troubleshooting

Common issues and solutions:

1. Face Recognition Issues
   - Ensure proper lighting conditions
   - Check webcam permissions
   - Verify face is clearly visible and centered

2. Database Issues
   - Run `python reset_db.py` to reset the database
   - Check database permissions in instance folder

3. Dependencies
   - Make sure all requirements are installed with correct versions
   - Some systems may need additional system packages for OpenCV

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.