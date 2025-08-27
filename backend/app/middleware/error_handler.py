from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Callable
import logging
import traceback
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self):
        self.error_counts = {}
        self.last_errors = []
    
    def log_error(self, error: Exception, request: Request = None):
        """Log error with context"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
        }
        
        if request:
            error_info.update({
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
            })
        
        # Store recent errors (keep last 100)
        self.last_errors.append(error_info)
        if len(self.last_errors) > 100:
            self.last_errors.pop(0)
        
        # Count error types
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        logger.error(f"Error occurred: {error_info}")
    
    def get_error_stats(self):
        """Get error statistics"""
        return {
            "error_counts": self.error_counts,
            "recent_errors": self.last_errors[-10:],  # Last 10 errors
            "total_errors": len(self.last_errors)
        }

# Global error handler instance
error_handler = ErrorHandler()

async def error_handling_middleware(request: Request, call_next: Callable):
    """
    Centralized error handling middleware
    """
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Log successful requests
        processing_time = time.time() - start_time
        if processing_time > 1.0:  # Log slow requests
            logger.warning(f"Slow request: {request.method} {request.url.path} took {processing_time:.2f}s")
        
        return response
        
    except HTTPException as e:
        # Handle FastAPI HTTP exceptions
        error_handler.log_error(e, request)
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": "HTTP Error",
                "message": e.detail,
                "status_code": e.status_code,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except Exception as e:
        # Handle unexpected errors
        error_handler.log_error(e, request)
        
        # Don't expose internal errors to clients
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred during processing",
                "timestamp": datetime.now().isoformat(),
                "request_id": str(hash(str(request.url) + str(time.time())))
            }
        )

def create_error_response(message: str, status_code: int = 400, details: dict = None):
    """
    Create standardized error response
    """
    error_response = {
        "error": True,
        "message": message,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        error_response["details"] = details
    
    return JSONResponse(status_code=status_code, content=error_response)

def create_success_response(data: dict, message: str = "Success"):
    """
    Create standardized success response
    """
    return {
        "error": False,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }