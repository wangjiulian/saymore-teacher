import pytest
from datetime import datetime, timedelta
from flask import url_for, session
from models.student import Student
from models.teacher import Teacher
from models.course import Course, CourseStatus, CourseType
from models.teacher_availability import TeacherAvailability
from models.sms_verification import SmsVerification


class TestAuthRoutes:
    """Test cases for authentication-related routes"""
    
    def test_login_page(self, client, captured_templates):
        """Test login page loads properly"""
        # Make a request to the login page
        response = client.get('/auth/login')
        
        # Check response is successful
        assert response.status_code == 200
        
        # Check the correct template was rendered
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == 'auth/login.html'
    
    def test_send_verification_code(self, client, db):
        """Test sending verification code for login"""
        # Create test request data
        data = {
            'phone': '13800138000'
        }
        
        # Send POST request to the verification endpoint
        response = client.post('/auth/send-code', data=data)
        
        # Check response is successful
        assert response.status_code == 200
        
        # Check response content
        json_data = response.get_json()
        assert json_data['success'] == True
        
        # Verify code was saved in database
        verification = SmsVerification.query.filter_by(phone='13800138000').first()
        assert verification is not None
    
    def test_login_with_code(self, client, db):
        """Test login with verification code"""
        # Create a teacher in the database
        teacher = Teacher(
            phone='13800138000',
            name='Test Teacher',
            nickname='Mr. Test'
        )
        db.session.add(teacher)
        
        # Add verification code
        now = int(datetime.now().timestamp())
        verification = SmsVerification(
            phone='13800138000',
            code='1233',  # Test code
            expiry_time=now + 300,  # 5 minutes from now
            created_at=now
        )
        db.session.add(verification)
        db.session.commit()
        
        # Attempt login
        response = client.post('/auth/login', data={
            'phone': '13800138000',
            'code': '1233'
        }, follow_redirects=True)
        
        # Check successful login
        assert response.status_code == 200
        # Should be redirected to profile page on success
        assert b'Profile' in response.data


class TestCourseRoutes:
    """Test cases for course-related routes"""
    
    def test_course_list(self, client, db, app):
        """Test course listing page"""
        # Create test teacher
        teacher = Teacher(
            phone='13800138000',
            name='Test Teacher',
            nickname='Mr. Test'
        )
        db.session.add(teacher)
        db.session.commit()
        
        # Set up logged in session
        with client.session_transaction() as sess:
            sess['_user_id'] = str(teacher.id)
        
        # Request course list page
        response = client.get('/courses/')
        
        # Check response
        assert response.status_code == 200
    
    def test_start_course(self, client, db):
        """Test starting a course"""
        # Create test teacher
        teacher = Teacher(
            phone='13800138000',
            name='Test Teacher',
            nickname='Mr. Test'
        )
        db.session.add(teacher)
        
        # Create test student
        student = Student(
            phone='13900139000',
            nickname='Test Student'
        )
        db.session.add(student)
        
        # Create test course
        now = int(datetime.now().timestamp())
        course = Course(
            name='Test Course',
            teacher_id=1,  # Teacher ID
            student_id=1,  # Student ID
            course_type=CourseType.REGULAR.value,
            status=CourseStatus.NOT_STARTED.value,
            start_time=now - 300,  # 5 minutes ago
            end_time=now + 2700  # 45 minutes from now
        )
        db.session.add(course)
        db.session.commit()
        
        # Set up logged in session as the teacher
        with client.session_transaction() as sess:
            sess['_user_id'] = str(teacher.id)
        
        # Send request to start course
        response = client.post(f'/courses/{course.id}/start')
        
        # Check response
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] == True
        
        # Verify course status was updated
        updated_course = Course.query.get(course.id)
        assert updated_course.status == CourseStatus.IN_PROGRESS.value


class TestAvailabilityRoutes:
    """Test cases for availability-related routes"""
    
    def test_add_availability_page(self, client, db):
        """Test displaying add availability page"""
        # Create test teacher
        teacher = Teacher(
            phone='13800138000',
            name='Test Teacher',
            nickname='Mr. Test'
        )
        db.session.add(teacher)
        db.session.commit()
        
        # Set up logged in session
        with client.session_transaction() as sess:
            sess['_user_id'] = str(teacher.id)
        
        # Request add availability page
        response = client.get('/availability/add')
        
        # Check response
        assert response.status_code == 200
    
    def test_list_availabilities(self, client, db):
        """Test listing availabilities"""
        # Create test teacher
        teacher = Teacher(
            phone='13800138000',
            name='Test Teacher',
            nickname='Mr. Test'
        )
        db.session.add(teacher)
        
        # Create some availability slots
        now = int(datetime.now().timestamp())
        tomorrow = now + 86400
        
        availability1 = TeacherAvailability(
            teacher_id=1,
            start_time=tomorrow,
            end_time=tomorrow + 3600,
            course_id=0
        )
        
        availability2 = TeacherAvailability(
            teacher_id=1,
            start_time=tomorrow + 7200,
            end_time=tomorrow + 10800,
            course_id=0
        )
        
        db.session.add_all([availability1, availability2])
        db.session.commit()
        
        # Set up logged in session
        with client.session_transaction() as sess:
            sess['_user_id'] = str(teacher.id)
        
        # Request availability list
        response = client.get('/availability/list?c=' + str(now))
        
        # Check response
        assert response.status_code == 200 