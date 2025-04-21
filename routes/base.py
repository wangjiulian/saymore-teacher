from flask import current_app, jsonify, request, Blueprint
import os
import uuid
import time
from datetime import datetime
import traceback
from flask_login import login_required, current_user


bp = Blueprint('upload', __name__, url_prefix='/upload')


@bp.route('/<file_type>', methods=['POST'])
@login_required
def upload_endpoint(file_type):
    """General file upload endpoint
    
    Supported file types:
    - avatar: Profile picture
    - video: Video
    - file: General file
    
    Returns:
        JSON response containing upload results
    """
    try:
        if file_type not in ['avatar', 'video', 'file']:
            return jsonify({'success': False, 'message': 'Unsupported file type'})
            
        file_key = 'file'
        if file_type == 'avatar':
            file_key = 'avatar'
        elif file_type == 'video':
            file_key = 'video'
            
        if file_key not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})
            
        file = request.files[file_key]
        
        # Set upload parameters
        if file_type == 'avatar':
            max_size = 2 * 1024 * 1024  # 2MB
            directory = 'avatars'
            file_type_cn = 'Profile Picture'
        elif file_type == 'video':
            max_size = 50 * 1024 * 1024  # 50MB
            directory = 'videos'
            file_type_cn = 'Video'
        else:
            max_size = 10 * 1024 * 1024  # 10MB
            directory = 'files'
            file_type_cn = 'File'
            
        # Call upload function
        result = upload_file(
            file=file,
            file_type=file_type_cn,
            directory=directory,
            max_size=max_size
        )
        
        # If upload successful, update user related fields
        if result['success'] and file_type in ['avatar', 'video']:
            teacher = current_user
            
            if file_type == 'avatar':
                teacher.avatar_url = result['url']
            elif file_type == 'video':
                teacher.video_url = result['url']
                
            teacher.save()
            
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Upload failed: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'Upload failed, please try again later'})


def upload_file(file, file_type='image', directory='common', max_size=None, allowed_extensions=None):
    """General file upload function, supports Aliyun OSS upload
    
    Args:
        file: File object (file from request.files)
        file_type: File type, used for logs and error messages ('image', 'video', etc.)
        directory: Upload directory, e.g. 'avatars', 'videos', etc.
        max_size: Maximum file size (bytes), None means no limit
        allowed_extensions: List of allowed file extensions, None means use default settings
        
    Returns:
        dict: Dictionary containing upload results
            {
                'success': True/False,
                'message': Success or error message
                'url': File URL (only when success=True)
            }
    """
    try:
        # Check if file exists
        if not file:
            return {'success': False, 'message': 'No file uploaded'}
            
        if file.filename == '':
            return {'success': False, 'message': 'No file selected'}
            
        # Set default allowed extensions
        if allowed_extensions is None:
            if file_type == 'Profile Picture' or file_type == 'image':
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            elif file_type == 'Video' or file_type == 'video':
                allowed_extensions = {'mp4', 'webm', 'mov', 'avi'}
            else:
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'txt'}
                
        # Check file type
        filename = file.filename
        if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            allowed_types = ', '.join([f'.{ext}' for ext in allowed_extensions])
            return {'success': False, 'message': f'Unsupported file type, please upload {file_type} in {allowed_types} format'}
            
        # Read file content
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Check file size
        if max_size is not None and len(file_content) > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return {'success': False, 'message': f'File size exceeds {max_size_mb}MB limit'}
            
        # Generate filename and path
        now = datetime.now()
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}_{int(time.time())}.{file_extension}"
        
        # OSS path format: uploads/type/year/month/filename
        oss_path = f"uploads/{directory}/{now.year}/{now.month:02d}/{unique_filename}"
        
        # Try to upload to Aliyun OSS
        file_url = None
        use_oss = current_app.config.get('UPLOAD_USE_OSS', False)
        
        if use_oss:
            try:
                import oss2
                # Get OSS configuration
                access_key_id = current_app.config.get('OSS_ACCESS_KEY_ID')
                access_key_secret = current_app.config.get('OSS_ACCESS_KEY_SECRET')
                bucket_name = current_app.config.get('OSS_BUCKET_NAME')
                endpoint = current_app.config.get('OSS_ENDPOINT')
                bucket_url = current_app.config.get('OSS_BUCKET_URL')
                
                # Check OSS configuration
                if all([access_key_id, access_key_secret, bucket_name, endpoint]):
                    # Initialize OSS client
                    auth = oss2.Auth(access_key_id, access_key_secret)
                    bucket = oss2.Bucket(auth, endpoint, bucket_name)
                    
                    # Set file header information
                    headers = {}
                    # Set Content-Type based on file extension
                    if file_extension in ['jpg', 'jpeg']:
                        headers['Content-Type'] = 'image/jpeg'
                    elif file_extension == 'png':
                        headers['Content-Type'] = 'image/png'
                    elif file_extension == 'gif':
                        headers['Content-Type'] = 'image/gif'
                    elif file_extension == 'mp4':
                        headers['Content-Type'] = 'video/mp4'
                    
                    # Upload file
                    if headers:
                        result = bucket.put_object(oss_path, file_content, headers=headers)
                    else:
                        result = bucket.put_object(oss_path, file_content)
                    
                    # Check upload result
                    if result.status == 200:
                        if bucket_url:
                            file_url = f"{bucket_url.rstrip('/')}/{oss_path}"
                        else:
                            file_url = f"https://{bucket_name}.{endpoint.replace('http://', '').replace('https://', '')}/{oss_path}"
                        current_app.logger.info(f"{file_type} successfully uploaded to OSS: {file_url}")
                    else:
                        current_app.logger.error(f"OSS upload failed: status code={result.status}")
            except ImportError:
                current_app.logger.warning("OSS SDK (oss2) not installed, will use local storage")
            except Exception as e:
                current_app.logger.error(f"OSS upload exception: {str(e)}")
        
        # If OSS upload failed or OSS is not used, save locally
        if not file_url:
            # Local storage path: static/uploads/type/filename
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', directory)
            os.makedirs(upload_dir, exist_ok=True)
            
            local_path = os.path.join(upload_dir, unique_filename)
            file.save(local_path)
            file_url = f"/static/uploads/{directory}/{unique_filename}"
            current_app.logger.info(f"{file_type} saved locally: {file_url}")
        
        return {
            'success': True, 
            'message': f'{file_type} uploaded successfully',
            'url': file_url
        }
    except Exception as e:
        current_app.logger.error(f"{file_type} upload failed: {str(e)}\n{traceback.format_exc()}")
        return {'success': False, 'message': f'{file_type} upload failed, please try again later'} 