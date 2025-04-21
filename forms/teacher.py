from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL

from models.subject import Subject


class TeacherProfileForm(FlaskForm):
    """
    Teacher Profile Edit Form
    """
    name = StringField('Name', validators=[
        DataRequired(message='Please enter your name'),
        Length(min=2, max=20, message='Name must be 2-20 characters long')
    ])

    nickname = StringField('Nickname', validators=[
        DataRequired(message='Please enter your nickname'),
        Length(max=20, message='Nickname cannot exceed 20 characters')
    ])

    gender = SelectField('Gender', choices=[
        (0, 'Unknown'),
        (1, 'Male'),
        (2, 'Female')
    ], coerce=int)

    phone = StringField('Phone Number', validators=[
        DataRequired(message='Please enter your phone number'),
        Length(min=11, max=11, message='Phone number must be 11 digits'),
        Regexp(r'^1[3-9]\d{9}$', message='Please enter a valid phone number')
    ], render_kw={"readonly": True})

    education_school = StringField('Alma Mater', validators=[
        Optional(),
        Length(max=50, message='School name cannot exceed 50 characters')
    ])

    education_level = SelectField('Education Level', choices=[
        (0, 'Unknown'),
        (1, 'Bachelor'),
        (2, 'Master'),
        (3, 'PhD')
    ], coerce=int)

    teaching_start_date = DateField('Teaching Start Date', validators=[
        Optional()
    ], format='%Y-%m-%d')

    teaching_experience = TextAreaField('Teaching Experience', validators=[
        Optional(),
        Length(max=5000, message='Teaching experience description cannot exceed 5000 characters')
    ])

    success_cases = TextAreaField('Success Stories', validators=[
        Optional(),
        Length(max=5000, message='Success stories description cannot exceed 5000 characters')
    ])

    teaching_achievements = TextAreaField('Teaching Achievements', validators=[
        Optional(),
        Length(max=5000, message='Teaching achievements description cannot exceed 5000 characters')
    ])

    background = TextAreaField('Personal Background', validators=[
        Optional(),
        Length(max=5000, message='Personal background description cannot exceed 5000 characters')
    ])

    subjects = SelectMultipleField('Subjects You Can Teach', coerce=int, validators=[
        DataRequired(message='Please select at least one subject you can teach')
    ])

    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(TeacherProfileForm, self).__init__(*args, **kwargs)

        # Get all subjects and organize by parent-child relationship
        self.subjects.choices = []

        try:
            # Get all top-level subjects (those without parent subjects)
            parent_subjects = Subject.query.filter(Subject.parent_id == 0).order_by(Subject.sort_order).all()

            from flask import current_app
            current_app.logger.info(f"Found {len(parent_subjects)} parent subjects")

            # First identify which parent subjects have children
            parents_with_children = set()

            for parent_subject in parent_subjects:
                # Check if this parent subject has child subjects
                children = Subject.query.filter_by(parent_id=parent_subject.id).order_by(Subject.sort_order).all()
                current_app.logger.info(f"Found {len(children)} children for parent subject {parent_subject.name}")

                if children:
                    # If it has child subjects, record this parent subject ID
                    parents_with_children.add(parent_subject.id)
                    # Add all child subjects, formatted as "Parent Subject Name - Child Subject Name"
                    for child in children:
                        self.subjects.choices.append((child.id, f"{parent_subject.name} - {child.name}"))
                else:
                    # If no child subjects, add the parent subject directly
                    self.subjects.choices.append((parent_subject.id, parent_subject.name))

            current_app.logger.info(f"Total subject choices: {len(self.subjects.choices)}")

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Failed to initialize subject options: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
