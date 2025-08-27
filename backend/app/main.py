from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import tempfile
import aiofiles
from pathlib import Path
from contextlib import asynccontextmanager

from .graph.schemas import ProcessingRequest, ProcessingResult
from .graph.workflow import process_medical_request, get_workflow_status
from .middleware.validation import validate_processing_request
from .middleware.error_handler import error_handling_middleware, error_handler, create_success_response
from .middleware.metrics import metrics_middleware, metrics_tracker

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Medical Processing API starting up...")
    print(f"🔑 OpenAI API Key configured: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    yield
    # Shutdown
    print("🛑 Medical Processing API shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Medical Information Processing API",
    description="LangGraph-powered API for processing medical audio and text data",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(error_handling_middleware)
app.middleware("http")(metrics_middleware)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Medical Information Processing API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "process": "/process - Main processing endpoint (URL-based audio)",
            "process_upload": "/process/upload - File upload processing endpoint",
            "health": "/health - Health check",
            "metrics": "/metrics - Performance metrics",
            "workflow": "/workflow/status - Workflow status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if OpenAI API key is configured
        api_key_configured = bool(os.getenv("OPENAI_API_KEY"))
        
        # Get workflow status
        workflow_status = get_workflow_status()
        
        from datetime import datetime
        uptime = datetime.now() - metrics_tracker.start_time if hasattr(metrics_tracker, 'start_time') else 0
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime.total_seconds() if hasattr(uptime, 'total_seconds') else 0,
            "api_key_configured": api_key_configured,
            "workflow_status": workflow_status["status"]
        }
        
        return health_status
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@app.post("/process")
async def process_request(request_data: ProcessingRequest):
    """
    Main endpoint for processing medical audio/text requests
    """
    try:
        # Validate request
        validation_result = validate_processing_request(
            audio_url=str(request_data.audio_url) if request_data.audio_url else None,
            text=request_data.text
        )
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Request validation failed",
                    "errors": validation_result["errors"]
                }
            )
        
        # Process the request through the LangGraph workflow
        result = await process_medical_request(request_data)
        
        # Return successful response
        return create_success_response(
            data=result.dict(),
            message="Medical information processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

@app.post("/process/upload")
async def process_uploaded_file(file: UploadFile = File(...)):
    """
    Process uploaded audio file for medical analysis
    """
    # Validate file type
    allowed_types = [
        "audio/mpeg", "audio/mp3",
        "audio/wav", "audio/wave", 
        "audio/mp4", "audio/m4a",
        "audio/aac", "audio/ogg",
        "audio/flac"
    ]
    
    allowed_extensions = [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".mp4"]
    
    if file.content_type not in allowed_types:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Unsupported file type",
                    "supported_types": "MP3, WAV, M4A, AAC, OGG, FLAC",
                    "received_type": file.content_type
                }
            )
    
    # Validate file size (25MB limit)
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
    file_content = await file.read()
    
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "File too large",
                "max_size": "25MB",
                "received_size": f"{len(file_content) / (1024*1024):.1f}MB"
            }
        )
    
    # Create temporary file
    temp_file = None
    try:
        # Get file extension for temporary file
        file_ext = Path(file.filename).suffix if file.filename else ".mp3"
        
        temp_file = tempfile.NamedTemporaryFile(
            suffix=file_ext,
            delete=False
        )
        
        # Write uploaded content to temporary file
        async with aiofiles.open(temp_file.name, 'wb') as f:
            await f.write(file_content)
        
        # Create processing request with the temporary file path
        # We'll modify the workflow to accept local file paths
        request_data = ProcessingRequest(
            audio_url=f"file://{temp_file.name}",
            text=None
        )
        
        # Process the request through the LangGraph workflow
        result = await process_medical_request(request_data)
        
        # Return successful response
        return create_success_response(
            data=result.dict(),
            message=f"Audio file '{file.filename}' processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File processing failed: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass

@app.get("/workflow/status")
async def get_workflow_info():
    """Get workflow status and information"""
    try:
        status = get_workflow_status()
        return create_success_response(
            data=status,
            message="Workflow status retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get API performance metrics"""
    try:
        metrics = metrics_tracker.get_full_metrics()
        return create_success_response(
            data=metrics,
            message="Metrics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/errors")
async def get_error_metrics():
    """Get error statistics"""
    try:
        error_stats = error_handler.get_error_stats()
        return create_success_response(
            data=error_stats,
            message="Error metrics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    )