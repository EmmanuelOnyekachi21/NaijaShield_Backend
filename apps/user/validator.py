from PIL import Image
from django.core.exceptions import ValidationError
import imghdr

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_image_file(uploaded_file):
    # Size check
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File size must be less than {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Extension Check
    name = getattr(uploaded_file, 'name', '')
    if '.' in name:
        ext = name.rsplit('.', 1)[1].lower()
    else:
        ext = None
    
    if not ext and ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("Unsupported file extension.  Allowed: jpg, jpeg, png")

    # Confirm file is a real image using Pillow
    try:
        uploaded_file.seek(0)
        img = image.open(uploaded_file)
        img.verify()
    except Exception as e:
        raise ValidationError("Invalid image file")
    finally:
        try:
            uploaded_file.seek(0)
        except Exception as e:
            pass


