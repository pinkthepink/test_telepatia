import aiofiles
import aiohttp
import tempfile
import os
from pathlib import Path
from typing import Optional

async def download_audio_file(url: str) -> Optional[str]:
    """
    Download audio file from URL or return local file path.
    Returns the local file path or None if download fails.
    """
    try:
        # Handle local file paths (from file uploads)
        if url.startswith('file://'):
            local_path = url.replace('file://', '')
            if os.path.exists(local_path):
                return local_path
            else:
                raise Exception(f"Local file not found: {local_path}")
        
        # Handle HTTP/HTTPS URLs (existing functionality)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: Failed to download audio file")
                
                # Get file extension from URL or content type
                content_type = response.headers.get('content-type', '')
                if 'audio' not in content_type:
                    # Try to get extension from URL
                    url_path = Path(url)
                    extension = url_path.suffix if url_path.suffix else '.mp3'
                else:
                    # Map content type to extension
                    type_mapping = {
                        'audio/mpeg': '.mp3',
                        'audio/wav': '.wav',
                        'audio/mp4': '.mp4',
                        'audio/m4a': '.m4a',
                        'audio/ogg': '.ogg'
                    }
                    extension = type_mapping.get(content_type, '.mp3')
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=extension, 
                    delete=False
                )
                
                # Download and save file
                async with aiofiles.open(temp_file.name, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                
                return temp_file.name
                
    except Exception as e:
        raise Exception(f"Failed to download audio file: {str(e)}")

def cleanup_temp_file(file_path: str, original_url: str = None) -> None:
    """Clean up temporary audio file."""
    try:
        if os.path.exists(file_path):
            # Only delete if it's not a pre-existing local file from upload
            # (uploaded files are handled by the upload endpoint)
            if original_url and not original_url.startswith('file://'):
                os.unlink(file_path)
            elif original_url and original_url.startswith('file://'):
                # This is an uploaded file - don't delete here as it's handled by upload endpoint
                pass
            else:
                # Fallback - delete the file
                os.unlink(file_path)
    except Exception:
        pass