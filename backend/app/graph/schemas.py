from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional, Union
from datetime import datetime
import re

class ProcessingRequest(BaseModel):
    audio_url: Optional[str] = Field(None, description="URL to audio file or local file path for transcription")
    text: Optional[str] = Field(None, description="Free text input for medical analysis")
    
    @field_validator('audio_url')
    @classmethod
    def validate_audio_url(cls, v):
        if v is None:
            return v
        
        # Allow file:// URLs for uploaded files
        if v.startswith('file://'):
            return v
            
        # Validate HTTP/HTTPS URLs
        if re.match(r'^https?://', v):
            # Use HttpUrl validation for HTTP/HTTPS URLs
            try:
                HttpUrl(v)
                return v
            except Exception:
                raise ValueError("Invalid HTTP/HTTPS URL format")
        
        raise ValueError("URL must be either a valid HTTP/HTTPS URL or a file:// path")
    
    @classmethod
    def validate_input(cls, values):
        if not values.get('audio_url') and not values.get('text'):
            raise ValueError("Either audio_url or text must be provided")
        return values

class PatientInfo(BaseModel):
    name: Optional[str] = Field(None, description="Patient's full name")
    age: Optional[int] = Field(None, ge=0, le=150, description="Patient's age in years")
    identification_number: Optional[str] = Field(None, description="Patient ID or document number")
    gender: Optional[str] = Field(None, description="Patient's gender")
    contact_info: Optional[str] = Field(None, description="Contact information")

class MedicalExtraction(BaseModel):
    symptoms: List[str] = Field(default_factory=list, description="List of identified symptoms")
    patient_info: PatientInfo = Field(default_factory=PatientInfo, description="Patient identification information")
    consultation_reason: str = Field("", description="Reason for medical consultation")
    extracted_text: str = Field("", description="Original processed text")

class DiagnosisResult(BaseModel):
    diagnosis: str = Field("", description="Medical diagnosis based on symptoms")
    treatment_plan: str = Field("", description="Recommended treatment plan")
    recommendations: str = Field("", description="Additional medical recommendations")

class ProcessingResult(BaseModel):
    transcription: str = Field("", description="Audio transcription result")
    medical_extraction: MedicalExtraction = Field(default_factory=MedicalExtraction)
    diagnosis_result: DiagnosisResult = Field(default_factory=DiagnosisResult)
    processing_time: float = Field(0.0, description="Total processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)

class WorkflowState(BaseModel):
    input_data: ProcessingRequest
    transcription: str = ""
    medical_extraction: MedicalExtraction = Field(default_factory=MedicalExtraction)
    diagnosis_result: DiagnosisResult = Field(default_factory=DiagnosisResult)
    processing_metadata: dict = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)