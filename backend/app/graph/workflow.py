from langgraph.graph import StateGraph, END
from typing import Dict, Any
import time

from .schemas import WorkflowState, ProcessingRequest, ProcessingResult
from .nodes import transcription_node, medical_extraction_node, diagnosis_node
from ..config.langfuse import start_trace, flush_traces, langfuse_enabled

def create_medical_workflow():
    """
    Create the LangGraph workflow that chains the three medical processing functions
    """
    
    # Define the workflow state graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("transcription", transcription_node)
    workflow.add_node("medical_extraction", medical_extraction_node)
    workflow.add_node("diagnosis", diagnosis_node)
    
    # Define the workflow edges
    workflow.set_entry_point("transcription")
    workflow.add_edge("transcription", "medical_extraction")
    workflow.add_edge("medical_extraction", "diagnosis")
    workflow.add_edge("diagnosis", END)
    
    # Compile the workflow
    return workflow.compile()

# Global workflow instance
medical_workflow = create_medical_workflow()

async def process_medical_request(request_data: ProcessingRequest) -> ProcessingResult:
    """
    Main function to process medical requests through the LangGraph workflow
    """
    start_time = time.time()
    
    # Create overall workflow trace
    workflow_trace = None
    if langfuse_enabled:
        workflow_trace = start_trace(
            name="medical_workflow",
            metadata={
                "workflow": "medical_processing",
                "has_audio": bool(request_data.audio_url),
                "has_text": bool(request_data.text),
                "text_length": len(request_data.text) if request_data.text else 0
            }
        )
    
    # Initialize workflow state
    initial_state = WorkflowState(
        input_data=request_data,
        processing_metadata={
            "start_time": start_time,
            "langfuse_trace_id": workflow_trace.id if workflow_trace else None
        }
    )
    
    try:
        # Run the workflow
        result = await medical_workflow.ainvoke(initial_state)
        
        # Calculate total processing time
        total_time = time.time() - start_time
        
        # Create the final result
        processing_result = ProcessingResult(
            transcription=result.get("transcription", ""),
            medical_extraction=result.get("medical_extraction"),
            diagnosis_result=result.get("diagnosis_result"),
            processing_time=total_time
        )
        
        # Update workflow trace with final results
        if workflow_trace:
            try:
                workflow_trace.update(
                    output={
                        "transcription_length": len(processing_result.transcription),
                        "symptoms_count": len(processing_result.medical_extraction.symptoms) if processing_result.medical_extraction else 0,
                        "diagnosis_generated": bool(processing_result.diagnosis_result.diagnosis) if processing_result.diagnosis_result else False,
                        "total_processing_time": total_time
                    },
                    metadata={
                        "success": True,
                        "node_timings": result.get("processing_metadata", {})
                    }
                )
                workflow_trace.end()
            except Exception as e:
                print(f"Warning: Failed to update workflow trace: {e}")
        
        # Flush traces to Langfuse
        if langfuse_enabled:
            flush_traces()
        
        return processing_result
        
    except Exception as e:
        # Handle workflow errors
        total_time = time.time() - start_time
        
        if workflow_trace:
            try:
                workflow_trace.update(
                    output={"error": str(e)},
                    metadata={
                        "success": False,
                        "total_processing_time": total_time,
                        "failed": True
                    }
                )
                workflow_trace.end()
            except Exception as trace_error:
                print(f"Warning: Failed to update error trace: {trace_error}")
        
        # Flush traces even on error
        if langfuse_enabled:
            flush_traces()
        
        error_result = ProcessingResult(
            transcription="Error occurred during processing",
            processing_time=total_time
        )
        raise Exception(f"Workflow execution failed: {str(e)}")

def get_workflow_status() -> Dict[str, Any]:
    """
    Get the current status of the workflow
    """
    return {
        "status": "active",
        "nodes": ["transcription", "medical_extraction", "diagnosis"],
        "description": "Medical information processing workflow"
    }