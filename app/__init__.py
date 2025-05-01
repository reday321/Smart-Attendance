from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = None  # Remove the default "Please log in" message
    
    from .models.user import User
    from .routes import auth, main, attendance
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(attendance.bp)
    
    with app.app_context():
        db.create_all()
    
    return app