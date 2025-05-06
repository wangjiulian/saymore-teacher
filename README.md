# SayMore Teacher Portal

A comprehensive web application for online English teachers to manage their schedules, courses, and students.

## Overview

SayMore Teacher Portal is designed for English teachers to efficiently manage their teaching activities. The platform facilitates course scheduling, student management, and teaching records tracking.

## Features

- **Account Management**: Secure login via phone verification
- **Profile Management**: Edit personal information, teaching experience, and qualifications
- **Course Management**: View, start, end, and cancel scheduled classes
- **Availability Settings**: Set and manage available teaching hours
- **Teaching Records**: Track teaching hours and compensation
- **Student Management**: View student information and progress

## Tech Stack

- **Backend**: Python/Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Database**: SQL (via SQLAlchemy ORM)
- **File Storage**: Local storage with optional Aliyun OSS support

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-organization/saymore-teacher.git
   cd saymore-teacher
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables (or create a `.env` file):
   ```
   FLASK_APP=create_app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_database_url
   ```

5. Initialize the database:
   ```
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

## Configuration

Key configuration options include:

- Database connection
- Aliyun OSS integration (optional)
- SMS verification service
- Session management

## Project Structure

- `/models/` - Database models and business logic
- `/routes/` - API endpoints and request handlers
- `/templates/` - HTML templates
- `/static/` - Static assets (CSS, JS, images)
- `/forms/` - Form definitions and validation
- `/utils/` - Utility functions

## Testing

The project includes a comprehensive test suite covering models, routes, and utility functions.

### Running Tests

To run the test suite:

```bash
# Make the test script executable
chmod +x run_tests.sh

# Run the tests with coverage reporting
./run_tests.sh
```

Or manually:

```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run tests with pytest
python -m pytest tests/
```

### Test Structure

- `tests/test_models.py` - Tests for database models
- `tests/test_routes.py` - Tests for route endpoints
- `tests/test_utils.py` - Tests for utility functions

## Development

To contribute to this project:

1. Create a feature branch
2. Implement your changes
3. Add tests (if applicable)
4. Submit a pull request

## Related Projects

- [SayMore Server](https://github.com/wangjiulian/saymore-server) - Backend API server for the SayMore platform
- [SayMore Server](https://github.com/wangjiulian/saymore-mini) - Frontend web app for the SayMore platform

## License

Copyright © 2025 SayMore. All rights reserved.
