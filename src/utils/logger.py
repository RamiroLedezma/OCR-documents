import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from src.config import settings

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """Log with structured data"""
        extra_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            **kwargs
        }
        
        log_message = f"{message} | {' | '.join(f'{k}={v}' for k, v in extra_data.items() if k not in ['timestamp', 'level'])}"
        getattr(self.logger, level.lower())(log_message)
    
    def info(self, message: str, **kwargs):
        self._log_structured('INFO', message, **kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        if error:
            kwargs['error_type'] = type(error).__name__
            kwargs['error_message'] = str(error)
        self._log_structured('ERROR', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log_structured('WARNING', message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log_structured('DEBUG', message, **kwargs)
    
    def document_processed(self, document_id: str, processing_time: float, success: bool, **kwargs):
        """Log document processing events"""
        self.info(
            "Document processed",
            document_id=document_id,
            processing_time_ms=processing_time * 1000,
            success=success,
            **kwargs
        )
    
    def ocr_request(self, image_size: int, model: str, tokens_used: Optional[int] = None, **kwargs):
        """Log OCR requests"""
        self.info(
            "OCR request processed",
            image_size_bytes=image_size,
            model=model,
            tokens_used=tokens_used,
            **kwargs
        )
    
    def database_operation(self, operation: str, table: str, success: bool, duration: float, **kwargs):
        """Log database operations"""
        self.info(
            "Database operation",
            operation=operation,
            table=table,
            success=success,
            duration_ms=duration * 1000,
            **kwargs
        )

# Global logger instances
logger = StructuredLogger(__name__)
ocr_logger = StructuredLogger('ocr')
db_logger = StructuredLogger('database')
api_logger = StructuredLogger('api') 