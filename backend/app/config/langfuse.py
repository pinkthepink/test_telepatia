import os

# Check if Langfuse is properly configured
def is_langfuse_configured():
    """Check if all required Langfuse environment variables are set"""
    required_vars = ["LANGFUSE_SECRET_KEY", "LANGFUSE_PUBLIC_KEY"]
    return all(os.getenv(var) for var in required_vars)

# Initialize Langfuse client using environment variables
def get_langfuse_client():
    """Initialize and return Langfuse client"""
    if not is_langfuse_configured():
        return None
        
    try:
        from langfuse import Langfuse
        # Langfuse will automatically use environment variables
        langfuse = Langfuse()
        return langfuse
    except ImportError:
        print("Warning: langfuse package not installed")
        return None
    except Exception as e:
        print(f"Warning: Failed to initialize Langfuse: {e}")
        return None

# Initialize callback handler for LangChain integration
def get_langfuse_callback_handler():
    """Get Langfuse callback handler for LangChain"""
    if not is_langfuse_configured():
        return None
        
    try:
        from langfuse.langchain import CallbackHandler
        # CallbackHandler will automatically use environment variables
        handler = CallbackHandler()
        return handler
    except ImportError:
        print("Warning: langfuse.langchain.CallbackHandler not available")
        return None
    except Exception as e:
        print(f"Warning: Failed to initialize Langfuse callback handler: {e}")
        return None

# Helper functions for tracing
def start_trace(name: str, metadata: dict = None):
    """Start a new trace span using direct span method"""
    client = get_langfuse_client()
    if not client:
        return None
        
    try:
        return client.start_span(name=name, metadata=metadata or {})
    except Exception as e:
        print(f"Warning: Failed to start trace {name}: {e}")
        return None

def start_generation(name: str, model: str = None, metadata: dict = None):
    """Start a new generation span for LLM calls"""
    client = get_langfuse_client()
    if not client:
        return None
        
    try:
        kwargs = {"name": name, "metadata": metadata or {}}
        if model:
            kwargs["model"] = model
        return client.start_generation(**kwargs)
    except Exception as e:
        print(f"Warning: Failed to start generation {name}: {e}")
        return None

def flush_traces():
    """Flush all traces to Langfuse"""
    client = get_langfuse_client()
    if client:
        try:
            client.flush()
        except Exception as e:
            print(f"Warning: Failed to flush traces: {e}")

# Global instances
langfuse_client = get_langfuse_client()
langfuse_enabled = langfuse_client is not None