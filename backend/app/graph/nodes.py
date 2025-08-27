import os
import time
from openai import OpenAI
from typing import Dict, Any
import json
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .schemas import WorkflowState, MedicalExtraction, PatientInfo, DiagnosisResult
from ..utils.audio_downloader import download_audio_file, cleanup_temp_file
from ..config.langfuse import get_langfuse_callback_handler, start_trace, start_generation, langfuse_enabled

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def transcription_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 1: Audio Transcription using OpenAI Whisper
    """
    start_time = time.time()
    
    # Create Langfuse trace for transcription
    trace = None
    if langfuse_enabled:
        trace = start_trace(
            name="transcription_node",
            metadata={
                "node": "transcription",
                "has_audio": bool(state.input_data.audio_url),
                "has_text": bool(state.input_data.text)
            }
        )
    
    try:
        # If text input is provided directly, skip transcription
        if state.input_data.text:
            transcription = state.input_data.text
            state.processing_metadata["transcription_time"] = 0
            
            if trace:
                try:
                    trace.update(
                        output={"transcription": transcription, "method": "direct_text"},
                        metadata={"processing_time": 0}
                    )
                except Exception as e:
                    print(f"Warning: Failed to update transcription trace: {e}")
                
        elif state.input_data.audio_url:
            # Create generation span for Whisper API call
            generation = None
            if langfuse_enabled:
                generation = start_generation(
                    name="whisper_transcription", 
                    model="whisper-1",
                    metadata={"audio_url": str(state.input_data.audio_url)}
                )
            
            # Download audio file
            audio_file_path = await download_audio_file(str(state.input_data.audio_url))
            
            # Transcribe using Whisper
            with open(audio_file_path, "rb") as audio_file:
                transcription_response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                transcription = transcription_response.text
            
            # Clean up temporary file
            cleanup_temp_file(audio_file_path, str(state.input_data.audio_url))
            
            processing_time = time.time() - start_time
            state.processing_metadata["transcription_time"] = processing_time
            
            if generation:
                try:
                    generation.update(
                        output={"transcription": transcription},
                        metadata={"processing_time": processing_time}
                    )
                    generation.end()
                except Exception as e:
                    print(f"Warning: Failed to update Whisper generation: {e}")
        else:
            raise ValueError("No audio URL or text provided")
        
        state.transcription = transcription
        
        if trace:
            try:
                trace.update(
                    output={"transcription": transcription},
                    metadata={"total_processing_time": time.time() - start_time}
                )
                trace.end()
            except Exception as e:
                print(f"Warning: Failed to update transcription trace: {e}")
        
        return {"transcription": transcription, "processing_metadata": state.processing_metadata}
        
    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        state.errors.append(error_msg)
        
        if trace:
            try:
                trace.update(
                    output={"error": error_msg},
                    metadata={"failed": True, "processing_time": time.time() - start_time}
                )
                trace.end()
            except Exception as trace_error:
                print(f"Warning: Failed to update error trace: {trace_error}")
        
        return {"errors": state.errors}

async def medical_extraction_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 2: Medical Information Extraction with structured output
    """
    start_time = time.time()
    
    # Create Langfuse trace for medical extraction
    trace = None
    if langfuse_enabled:
        trace = start_trace(
            name="medical_extraction_node",
            metadata={
                "node": "medical_extraction",
                "text_length": len(state.transcription) if state.transcription else 0
            }
        )
    
    try:
        # Create generation for LLM call
        generation = None
        if langfuse_enabled:
            generation = start_generation(
                name="medical_extraction_llm",
                model="gpt-4",
                metadata={"temperature": 0.1, "purpose": "medical_extraction"}
            )
        
        # Get callback handler for LangChain integration
        callbacks = []
        if langfuse_enabled:
            langfuse_handler = get_langfuse_callback_handler()
            if langfuse_handler:
                callbacks.append(langfuse_handler)
        
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            callbacks=callbacks
        )
        
        extraction_prompt = f"""
        Analyze the following medical text and extract structured information.
        Return ONLY a valid JSON object with the following structure:
        
        {{
            "symptoms": ["symptom1", "symptom2", ...],
            "patient_info": {{
                "name": "patient name or null",
                "age": age_number_or_null,
                "identification_number": "id or null",
                "gender": "gender or null",
                "contact_info": "contact or null"
            }},
            "consultation_reason": "brief reason for consultation",
            "extracted_text": "the original text"
        }}
        
        Text to analyze: {state.transcription}
        
        JSON:
        """
        
        response = llm.invoke([HumanMessage(content=extraction_prompt)])
        
        # Update generation with response
        if generation:
            try:
                generation.update(
                    input=extraction_prompt,
                    output=response.content,
                    metadata={"response_length": len(response.content)}
                )
                generation.end()
            except Exception as e:
                print(f"Warning: Failed to update extraction generation: {e}")
        
        # Parse the JSON response
        try:
            extracted_data = json.loads(response.content.strip())
            
            # Create structured objects
            patient_info = PatientInfo(**extracted_data.get("patient_info", {}))
            medical_extraction = MedicalExtraction(
                symptoms=extracted_data.get("symptoms", []),
                patient_info=patient_info,
                consultation_reason=extracted_data.get("consultation_reason", ""),
                extracted_text=extracted_data.get("extracted_text", state.transcription)
            )
            
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            medical_extraction = MedicalExtraction(
                symptoms=["Unable to parse symptoms"],
                patient_info=PatientInfo(),
                consultation_reason="Unable to parse consultation reason",
                extracted_text=state.transcription
            )
        
        state.medical_extraction = medical_extraction
        processing_time = time.time() - start_time
        state.processing_metadata["extraction_time"] = processing_time
        
        if trace:
            try:
                trace.update(
                    output={
                        "symptoms_count": len(medical_extraction.symptoms),
                        "patient_info": medical_extraction.patient_info.dict(),
                        "consultation_reason": medical_extraction.consultation_reason
                    },
                    metadata={"processing_time": processing_time}
                )
                trace.end()
            except Exception as e:
                print(f"Warning: Failed to update extraction trace: {e}")
        
        return {
            "medical_extraction": medical_extraction,
            "processing_metadata": state.processing_metadata
        }
        
    except Exception as e:
        error_msg = f"Medical extraction failed: {str(e)}"
        state.errors.append(error_msg)
        
        if trace:
            try:
                trace.update(
                    output={"error": error_msg},
                    metadata={"failed": True, "processing_time": time.time() - start_time}
                )
                trace.end()
            except Exception as trace_error:
                print(f"Warning: Failed to update error trace: {trace_error}")
        
        return {"errors": state.errors}

async def diagnosis_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 3: Diagnosis Generation
    """
    start_time = time.time()
    
    # Create Langfuse trace for diagnosis generation
    trace = None
    if langfuse_enabled:
        trace = start_trace(
            name="diagnosis_node",
            metadata={
                "node": "diagnosis_generation",
                "symptoms_count": len(state.medical_extraction.symptoms) if state.medical_extraction else 0
            }
        )
    
    try:
        # Create generation for LLM call
        generation = None
        if langfuse_enabled:
            generation = start_generation(
                name="diagnosis_generation_llm",
                model="gpt-4",
                metadata={"temperature": 0.2, "purpose": "diagnosis_generation"}
            )
        
        # Get callback handler for LangChain integration
        callbacks = []
        if langfuse_enabled:
            langfuse_handler = get_langfuse_callback_handler()
            if langfuse_handler:
                callbacks.append(langfuse_handler)
        
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            callbacks=callbacks
        )
        
        # Format symptoms and patient info for diagnosis
        symptoms_text = ", ".join(state.medical_extraction.symptoms) if state.medical_extraction.symptoms else "No specific symptoms identified"
        patient_age = state.medical_extraction.patient_info.age or "unknown"
        patient_gender = state.medical_extraction.patient_info.gender or "unknown"
        consultation_reason = state.medical_extraction.consultation_reason or "General consultation"
        
        diagnosis_prompt = f"""
        Based on the following medical information, provide a comprehensive medical assessment:
        
        Patient Information:
        - Age: {patient_age}
        - Gender: {patient_gender}
        - Consultation Reason: {consultation_reason}
        
        Symptoms: {symptoms_text}
        
        Please provide:
        1. A possible diagnosis (be conservative and suggest further evaluation when appropriate)
        2. A treatment plan with specific recommendations
        3. Additional recommendations for care or follow-up
        
        Important: This is for educational/demo purposes only. Always emphasize the need for proper medical consultation.
        
        Format your response as:
        
        DIAGNOSIS:
        [Your diagnosis here]
        
        TREATMENT PLAN:
        [Your treatment plan here]
        
        RECOMMENDATIONS:
        [Your recommendations here]
        """
        
        response = llm.invoke([HumanMessage(content=diagnosis_prompt)])
        diagnosis_text = response.content
        
        # Update generation with response
        if generation:
            try:
                generation.update(
                    input=diagnosis_prompt,
                    output=diagnosis_text,
                    metadata={"response_length": len(diagnosis_text)}
                )
                generation.end()
            except Exception as e:
                print(f"Warning: Failed to update diagnosis generation: {e}")
        
        # Parse the structured response
        lines = diagnosis_text.split('\n')
        diagnosis = ""
        treatment_plan = ""
        recommendations = ""
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("DIAGNOSIS:"):
                current_section = "diagnosis"
                diagnosis += line.replace("DIAGNOSIS:", "").strip() + "\n"
            elif line.startswith("TREATMENT PLAN:"):
                current_section = "treatment"
                treatment_plan += line.replace("TREATMENT PLAN:", "").strip() + "\n"
            elif line.startswith("RECOMMENDATIONS:"):
                current_section = "recommendations"
                recommendations += line.replace("RECOMMENDATIONS:", "").strip() + "\n"
            elif current_section == "diagnosis":
                diagnosis += line + "\n"
            elif current_section == "treatment":
                treatment_plan += line + "\n"
            elif current_section == "recommendations":
                recommendations += line + "\n"
        
        diagnosis_result = DiagnosisResult(
            diagnosis=diagnosis.strip(),
            treatment_plan=treatment_plan.strip(),
            recommendations=recommendations.strip()
        )
        
        state.diagnosis_result = diagnosis_result
        processing_time = time.time() - start_time
        state.processing_metadata["diagnosis_time"] = processing_time
        
        if trace:
            try:
                trace.update(
                    output={
                        "diagnosis": diagnosis_result.diagnosis[:200] + "..." if len(diagnosis_result.diagnosis) > 200 else diagnosis_result.diagnosis,
                        "treatment_plan": diagnosis_result.treatment_plan[:200] + "..." if len(diagnosis_result.treatment_plan) > 200 else diagnosis_result.treatment_plan,
                        "recommendations": diagnosis_result.recommendations[:200] + "..." if len(diagnosis_result.recommendations) > 200 else diagnosis_result.recommendations
                    },
                    metadata={"processing_time": processing_time}
                )
                trace.end()
            except Exception as e:
                print(f"Warning: Failed to update diagnosis trace: {e}")
        
        return {
            "diagnosis_result": diagnosis_result,
            "processing_metadata": state.processing_metadata
        }
        
    except Exception as e:
        error_msg = f"Diagnosis generation failed: {str(e)}"
        state.errors.append(error_msg)
        
        if trace:
            try:
                trace.update(
                    output={"error": error_msg},
                    metadata={"failed": True, "processing_time": time.time() - start_time}
                )
                trace.end()
            except Exception as trace_error:
                print(f"Warning: Failed to update error trace: {trace_error}")
        
        return {"errors": state.errors}