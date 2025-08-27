from fastapi import HTTPException, Request
from pydantic import ValidationError
from typing import Callable, Any
import re
from urllib.parse import urlparse

def validate_audio_url(url: str) -> bool:
    """Validate if the URL is a valid audio file URL"""
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return False
        
        # Check for common audio file extensions
        audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.wma']
        path_lower = parsed.path.lower()
        
        # Accept if it has audio extension or no extension (might be dynamic URL)
        has_audio_ext = any(path_lower.endswith(ext) for ext in audio_extensions)
        has_no_ext = '.' not in parsed.path.split('/')[-1]
        
        return has_audio_ext or has_no_ext
        
    except Exception:
        return False

def validate_text_input(text: str) -> bool:
    """Validate text input for medical processing"""
    if not text or not text.strip():
        return False
    
    # Basic validation - text should be reasonable length
    if len(text.strip()) < 10:
        return False
        
    if len(text) > 10000:  # Reasonable limit
        return False
    
    return True

async def request_validation_middleware(request: Request, call_next: Callable) -> Any:
    """
    Middleware for request validation
    """
    try:
        # Skip validation for health check and metrics endpoints
        if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            response = await call_next(request)
            return response
        
        # For the main processing endpoint
        if request.url.path == "/process" and request.method == "POST":
            body = await request.body()
            
            # Basic content-length check
            if len(body) > 50 * 1024 * 1024:  # 50MB limit
                raise HTTPException(status_code=413, detail="Request too large")
            
        response = await call_next(request)
        return response
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Request validation failed: {str(e)}")

def validate_processing_request(audio_url: str = None, text: str = None) -> dict:
    """
    Validate processing request parameters
    """
    errors = []
    
    if not audio_url and not text:
        errors.append("Either audio_url or text must be provided")
    
    if audio_url and not validate_audio_url(audio_url):
        errors.append("Invalid audio URL format or unsupported file type")
    
    if text and not validate_text_input(text):
        errors.append("Text input is too short (minimum 10 characters) or too long (maximum 10,000 characters)")
    
    if audio_url and text:
        errors.append("Please provide either audio_url OR text, not both")
    
    return {"valid": len(errors) == 0, "errors": errors}