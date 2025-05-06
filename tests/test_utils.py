import pytest
import io
import os
from datetime import datetime, timedelta
from flask import current_app
from unittest.mock import patch, MagicMock

from utils.sms import send_verification_code
from routes.base import upload_file


class TestSmsUtils:
    """Test cases for SMS utility functions"""
    
    @patch('utils.sms.requests.post')
    def test_send_verification_code(self, mock_post, app):
        """Test sending SMS verification code"""
        # Mock the response from SMS API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': 0, 'message': 'success'}
        mock_post.return_value = mock_response
        
        # Call the function
        with app.app_context():
            result = send_verification_code('13800138000', '1234')
        
        # Verify results
        assert result['success'] == True
        assert 'code' in result
        
        # Verify mock was called correctly
        mock_post.assert_called_once()


class TestFileUploadUtils:
    """Test cases for file upload utilities"""
    
    def test_upload_file_validation(self, app):
        """Test file upload validation"""
        with app.app_context():
            # Test with empty file
            result = upload_file(None, file_type='image')
            assert result['success'] == False
            assert 'No file uploaded' in result['message']
            
            # Create a mock file with empty filename
            mock_file = MagicMock()
            mock_file.filename = ''
            result = upload_file(mock_file, file_type='image')
            assert result['success'] == False
            assert 'No file selected' in result['message']
    
    def test_upload_file_extension_validation(self, app):
        """Test file extension validation"""
        with app.app_context():
            # Create a mock file with invalid extension
            mock_file = MagicMock()
            mock_file.filename = 'test.xyz'
            mock_file.read.return_value = b'test file content'
            
            result = upload_file(mock_file, file_type='image')
            assert result['success'] == False
            assert 'Unsupported file type' in result['message']
    
    def test_upload_file_size_validation(self, app):
        """Test file size validation"""
        with app.app_context():
            # Create a mock file with valid extension but exceeding size limit
            mock_file = MagicMock()
            mock_file.filename = 'test.jpg'
            # Create a file content larger than 1MB
            mock_file.read.return_value = b'x' * (1024 * 1024 + 1)
            
            result = upload_file(mock_file, file_type='image', max_size=1024 * 1024)
            assert result['success'] == False
            assert 'File size exceeds' in result['message']
    
    @patch('os.makedirs')
    @patch('routes.base.current_app')
    def test_upload_file_local_storage(self, mock_app, mock_makedirs, app):
        """Test local file storage when OSS is not used"""
        with app.app_context():
            # Configure mock app
            mock_app.config.get.return_value = False  # UPLOAD_USE_OSS=False
            mock_app.root_path = '/app'
            
            # Create a mock file
            mock_file = MagicMock()
            mock_file.filename = 'test.jpg'
            mock_file.read.return_value = b'test file content'
            
            # Mock file save method
            mock_file.save = MagicMock()
            
            # Call upload function
            with patch('routes.base.current_app', mock_app):
                result = upload_file(mock_file, file_type='image', directory='test')
            
            # Verify results
            assert result['success'] == True
            assert 'uploaded successfully' in result['message']
            assert 'url' in result
            
            # Verify directory was created
            mock_makedirs.assert_called_once()
            # Verify file was saved
            mock_file.save.assert_called_once() 