# Smart Attendance System with Face Recognition

A web-based attendance management system that uses face recognition technology to automate attendance tracking for educational institutions. The system provides a modern, secure, and efficient way to track student attendance using facial recognition, with role-based access for students, teachers, and administrators.

## Key Features

- **Face Recognition**
  - Automated attendance marking using real-time face detection
  - Secure face encoding storage
  - Confidence-based verification (70% threshold)
  - Support for proper lighting detection

- **User Management**
  - Role-based access (Student, Teacher, Admin)
  - Secure user authentication
  - Profile management with password protection
  - Department-based organization

- **Course Management**
  - Course creation and scheduling
  - Student enrollment system with approval workflow
  - Weekly schedule management
  - Classroom assignment

- **Attendance Tracking**
  - Real-time attendance marking
  - Detailed attendance reports
  - Course-wise attendance statistics
  - Overall attendance monitoring
  - Bangladesh timezone support (UTC+6)

- **Dashboard & Analytics**
  - Role-specific dashboards
  - Visual attendance statistics
  - Course progress tracking
  - Real-time notifications
  - Interactive charts and reports

## Technologies Used

- **Backend Framework**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy 3.1.1
- **Frontend**: HTML5, Bootstrap 5, Chart.js
- **Face Recognition**: OpenCV 4.6.0+, face-recognition 1.3.0
- **Authentication**: Flask-Login 0.6.2
- **Image Processing**: Pillow 10.0.0, NumPy 1.24.3

## Prerequisites

- Python 3.10 or higher
- Webcam access for face recognition
- Sufficient storage for face encodings
- Windows/Linux/MacOS supported

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Smart-Attendance-System
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
.\\venv\\Scripts\\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python reset_db.py
```

5. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
Smart-Attendance-System/
├── app/
│   ├── models/              # Database models
│   │   ├── user.py         # User model
│   │   └── attendance.py   # Course and attendance models
│   ├── routes/             # Route handlers
│   │   ├── auth.py        # Authentication routes
│   │   ├── main.py        # Dashboard routes
│   │   └── attendance.py  # Attendance management
│   ├── static/            # Static assets
│   │   ├── css/          # Stylesheets
│   │   └── images/       # Images and icons
│   └── templates/         # HTML templates
│       ├── attendance/    # Attendance-related pages
│       ├── auth/         # Authentication pages
│       └── main/         # Dashboard templates
├── instance/              # Database instance
├── requirements.txt       # Project dependencies
├── reset_db.py           # Database initialization
└── run.py               # Application entry point
```

## User Roles & Features

### Student
- Register and manage profile
- Register face for attendance
- View and enroll in available courses
- Mark attendance using face recognition
- View personal attendance statistics
- Receive enrollment notifications

### Teacher
- Create and manage courses
- Set course schedules and classrooms
- Approve/reject student enrollments
- View detailed attendance reports
- Monitor student attendance rates

### Admin
- Access system-wide statistics
- Monitor all courses and users
- View comprehensive attendance data
- System management capabilities

## Security Features

- Face recognition with confidence threshold
- Secure password hashing with Werkzeug
- Role-based access control
- Protected route authentication
- Session management
- CSRF protection
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Face Recognition library contributors
- Flask framework community
- Bootstrap team for the UI components