import pytest
from datetime import datetime, date, timedelta
from models.student import Student
from models.teacher import Teacher
from models.course import Course, CourseStatus, CourseType
from models.subject import Subject
from models.teacher_availability import TeacherAvailability


class TestStudentModel:
    """Test cases for the Student model"""
    
    def test_student_creation(self, db):
        """Test creating a new student record"""
        # Create a sample student
        student = Student(
            phone="13800138000",
            nickname="Test Student",
            gender=1,  # Male
            birth_date=date(2000, 1, 1),
            student_type=2,  # Elementary Student
            english_level=3,  # Can Speak Complete Sentences
            learning_purpose=3,  # General English Proficiency
        )
        
        # Add to database and commit
        db.session.add(student)
        db.session.commit()
        
        # Retrieve the student from database
        saved_student = Student.query.filter_by(phone="13800138000").first()
        
        # Verify student was saved correctly
        assert saved_student is not None
        assert saved_student.nickname == "Test Student"
        assert saved_student.gender == 1
        assert saved_student.student_type == 2
        assert saved_student.english_level == 3
    
    def test_gender_text(self):
        """Test the gender text helper method"""
        assert Student.get_gender_text(0) == "Unspecified"
        assert Student.get_gender_text(1) == "Male"
        assert Student.get_gender_text(2) == "Female"
        assert Student.get_gender_text(999) == "Unknown"  # Invalid value
    
    def test_student_type_text(self):
        """Test the student type text helper method"""
        assert Student.get_student_type_text(1) == "Preschooler"
        assert Student.get_student_type_text(2) == "Elementary Student"
        assert Student.get_student_type_text(3) == "Middle School Student"
        assert Student.get_student_type_text(4) == "High School Student"
        assert Student.get_student_type_text(5) == "College Student"
        assert Student.get_student_type_text(6) == "Professional"
        assert Student.get_student_type_text(999) == "Unknown"  # Invalid value


class TestTeacherModel:
    """Test cases for the Teacher model"""
    
    def test_teacher_creation(self, db):
        """Test creating a new teacher record"""
        # Create a sample teacher
        teacher = Teacher(
            phone="13900139000",
            name="Test Teacher",
            nickname="Mr. Test",
            gender=1,  # Male
            education_level=2,  # Master
            teaching_start_date=date(2018, 1, 1),
            teaching_experience="Experienced teacher with 5 years of teaching",
            course_hours=100.5
        )
        
        # Add to database and commit
        db.session.add(teacher)
        db.session.commit()
        
        # Retrieve the teacher from database
        saved_teacher = Teacher.query.filter_by(phone="13900139000").first()
        
        # Verify teacher was saved correctly
        assert saved_teacher is not None
        assert saved_teacher.name == "Test Teacher"
        assert saved_teacher.nickname == "Mr. Test"
        assert saved_teacher.gender == 1
        assert saved_teacher.education_level == 2
        assert saved_teacher.course_hours == 100.5


class TestCourseModel:
    """Test cases for the Course model"""
    
    def test_course_creation(self, db):
        """Test creating a new course record"""
        # Create a student and teacher
        student = Student(phone="13800138000", nickname="Test Student")
        teacher = Teacher(phone="13900139000", name="Test Teacher", nickname="Mr. Test")
        db.session.add_all([student, teacher])
        db.session.commit()
        
        # Get current timestamp
        now = int(datetime.now().timestamp())
        course_start = now + 3600  # 1 hour from now
        course_end = now + 3600 + 3000  # 50 minutes after start
        
        # Create a course
        course = Course(
            name="English Conversation Practice",
            teacher_id=teacher.id,
            student_id=student.id,
            course_type=CourseType.REGULAR.value,
            status=CourseStatus.NOT_STARTED.value,
            start_time=course_start,
            end_time=course_end
        )
        
        # Add to database and commit
        db.session.add(course)
        db.session.commit()
        
        # Retrieve the course from database
        saved_course = Course.query.filter_by(name="English Conversation Practice").first()
        
        # Verify course was saved correctly
        assert saved_course is not None
        assert saved_course.teacher_id == teacher.id
        assert saved_course.student_id == student.id
        assert saved_course.status == CourseStatus.NOT_STARTED.value
        assert saved_course.start_time == course_start
        assert saved_course.end_time == course_end
    
    def test_course_status_text(self, db):
        """Test the course status text helper method"""
        # Create a sample course
        course = Course(
            name="Test Course",
            status=CourseStatus.NOT_STARTED.value
        )
        
        # Test status text
        assert course.get_status_text() == "Pending Class"
        
        # Change status and test again
        course.status = CourseStatus.IN_PROGRESS.value
        assert course.get_status_text() == "In Progress"
        
        course.status = CourseStatus.COMPLETED.value
        assert course.get_status_text() == "Completed"
        
        course.status = CourseStatus.CANCELLED.value
        assert course.get_status_text() == "Cancelled"


class TestTeacherAvailabilityModel:
    """Test cases for the TeacherAvailability model"""
    
    def test_availability_creation(self, db):
        """Test creating a new teacher availability record"""
        # Create a teacher
        teacher = Teacher(phone="13900139000", name="Test Teacher")
        db.session.add(teacher)
        db.session.commit()
        
        # Get current timestamp
        now = int(datetime.now().timestamp())
        tomorrow = now + 86400  # 24 hours from now
        
        # Create availability
        availability = TeacherAvailability(
            teacher_id=teacher.id,
            start_time=tomorrow,
            end_time=tomorrow + 3600,  # 1 hour duration
            is_booked=False
        )
        
        # Add to database and commit
        db.session.add(availability)
        db.session.commit()
        
        # Retrieve the availability from database
        saved_availability = TeacherAvailability.query.filter_by(teacher_id=teacher.id).first()
        
        # Verify availability was saved correctly
        assert saved_availability is not None
        assert saved_availability.teacher_id == teacher.id
        assert saved_availability.start_time == tomorrow
        assert saved_availability.end_time == tomorrow + 3600
        assert saved_availability.is_booked == False
    
    def test_is_booked_method(self, db):
        """Test the is_booked method of TeacherAvailability"""
        # Create availability without a course ID
        availability = TeacherAvailability(
            teacher_id=1,
            start_time=int(datetime.now().timestamp()) + 3600,
            end_time=int(datetime.now().timestamp()) + 7200,
            course_id=0  # No course assigned
        )
        
        # Verify not booked
        assert availability.is_booked() == False
        
        # Assign a course ID
        availability.course_id = 123
        
        # Verify now booked
        assert availability.is_booked() == True 