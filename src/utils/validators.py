import base64
import io
import re
from typing import Optional, Tuple, Dict, Any
from PIL import Image
from src.config import settings
from src.utils.logger import logger

class ValidationError(Exception):
    """Custom validation error"""
    pass

class SecurityError(Exception):
    """Custom security error"""
    pass

class ImageValidator:
    """Validator for image inputs"""
    
    ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP', 'BMP'}
    MIN_DIMENSIONS = (100, 100)
    MAX_DIMENSIONS = (4000, 4000)
    
    @staticmethod
    def validate_base64(base64_string: str) -> str:
        """Validate base64 string format"""
        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:'):
                base64_string = base64_string.split(',')[1]
            
            # Validate base64 format
            base64.b64decode(base64_string, validate=True)
            return base64_string
        except Exception as e:
            logger.error("Invalid base64 format", error=e)
            raise ValidationError("Invalid base64 format")
    
    @staticmethod
    def validate_image_content(base64_string: str) -> Tuple[Image.Image, Dict[str, Any]]:
        """Validate image content and return image with metadata"""
        try:
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Check file size
            if len(image_data) > settings.MAX_FILE_SIZE:
                raise ValidationError(f"Image size exceeds limit ({settings.MAX_FILE_SIZE} bytes)")
            
            # Open and validate image
            image = Image.open(io.BytesIO(image_data))
            
            # Check format
            if image.format not in ImageValidator.ALLOWED_FORMATS:
                raise ValidationError(f"Unsupported image format: {image.format}")
            
            # Check dimensions
            width, height = image.size
            if width < ImageValidator.MIN_DIMENSIONS[0] or height < ImageValidator.MIN_DIMENSIONS[1]:
                raise ValidationError(f"Image too small. Minimum: {ImageValidator.MIN_DIMENSIONS}")
            
            if width > ImageValidator.MAX_DIMENSIONS[0] or height > ImageValidator.MAX_DIMENSIONS[1]:
                raise ValidationError(f"Image too large. Maximum: {ImageValidator.MAX_DIMENSIONS}")
            
            # Image metadata
            metadata = {
                'format': image.format,
                'size': image.size,
                'mode': image.mode,
                'file_size_bytes': len(image_data)
            }
            
            logger.info("Image validation successful", **metadata)
            return image, metadata
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error("Image validation failed", error=e)
            raise ValidationError(f"Invalid image: {str(e)}")

class DocumentValidator:
    """Validator for document-related data"""
    
    DOCUMENT_TYPES = {'cedula', 'pasaporte', 'licencia', 'tarjeta_identidad'}
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate filename for security"""
        # Remove path traversal attempts
        clean_filename = re.sub(r'[/\\]', '', filename)
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'\.\.',  # Path traversal
            r'[<>:"|?*]',  # Windows illegal characters
            r'^\.',  # Hidden files
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, clean_filename):
                raise SecurityError(f"Dangerous filename pattern detected: {filename}")
        
        # Length check
        if len(clean_filename) > 255:
            raise ValidationError("Filename too long")
        
        return clean_filename
    
    @staticmethod
    def validate_extracted_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted document data"""
        validated_data = {}
        
        # Validate document type
        if 'tipo_documento' in data and data['tipo_documento']:
            doc_type = data['tipo_documento'].lower()
            if doc_type not in DocumentValidator.DOCUMENT_TYPES:
                logger.warning(f"Unknown document type: {doc_type}")
            validated_data['tipo_documento'] = doc_type
        
        # Validate and sanitize text fields
        text_fields = ['nombres', 'apellidos', 'lugar_nacimiento', 'lugar_expedicion']
        for field in text_fields:
            if field in data and data[field]:
                # Remove potentially dangerous characters
                clean_value = re.sub(r'[<>"\']', '', str(data[field]))
                clean_value = clean_value.strip()
                if clean_value:
                    validated_data[field] = clean_value
        
        # Validate document number
        if 'numero_documento' in data and data['numero_documento']:
            doc_num = re.sub(r'[^\w\-]', '', str(data['numero_documento']))
            if len(doc_num) >= 5:  # Minimum reasonable length
                validated_data['numero_documento'] = doc_num
        
        # Validate dates
        date_fields = ['fecha_nacimiento', 'fecha_expedicion']
        for field in date_fields:
            if field in data and data[field]:
                date_value = DocumentValidator._validate_date(data[field])
                if date_value:
                    validated_data[field] = date_value
        
        return validated_data
    
    @staticmethod
    def _validate_date(date_str: str) -> Optional[str]:
        """Validate date format"""
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, date_str):
                return date_str
        
        return None

class SecurityValidator:
    """Security-related validations"""
    
    @staticmethod
    def validate_request_origin(request_data: Dict[str, Any]) -> bool:
        """Validate request for security threats"""
        # Check for suspicious patterns in text data
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'eval\(',
            r'exec\(',
            r'import\s+os',
            r'__import__',
        ]
        
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in suspicious_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        logger.warning(f"Suspicious pattern detected in {key}: {pattern}")
                        raise SecurityError(f"Suspicious content detected in {key}")
        
        return True 