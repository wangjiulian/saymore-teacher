import os
import pytest
import tempfile
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from create_app import create_app
from extensions import db as _db


@pytest.fixture(scope='session')
def app():
    """
    Create a Flask app configured for testing.
    This fixture is used for the entire test session.
    """
    # Create a temporary file to use as a test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure the app for testing
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF protection for testing
        'SERVER_NAME': 'localhost.localdomain',  # Required for url_for to work in tests
    })
    
    # Establish application context
    with app.app_context():
        # Initialize database tables
        _db.create_all()
        
        yield app
        
        # Clean up after tests
        _db.session.remove()
        _db.drop_all()
    
    # Close and remove the temporary database file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def db(app):
    """
    Provide a database session for tests.
    Create a fresh database for each test function.
    """
    with app.app_context():
        _db.create_all()
        
        yield _db
        
        # Rollback any uncommitted changes
        _db.session.rollback()
        # Clear the database at the end of each test
        _db.drop_all()
        _db.create_all()


@pytest.fixture(scope='function')
def client(app):
    """
    Create a test client for the Flask application.
    This fixture is scoped to each test function.
    """
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(scope='function')
def captured_templates(app):
    """
    Fixture to capture templates rendered during a test.
    """
    recorded = []
    
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    
    from flask import template_rendered
    template_rendered.connect(record, app)
    
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app) 