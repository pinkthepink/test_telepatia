# Medical Information Processing Application

A full-stack web application that processes audio and text inputs to extract medical information, generate diagnoses, and provide treatment recommendations using AI/LLM integration with LangGraph workflows.

## 🏗️ Architecture

### Technologies Used
- **Backend**: Python FastAPI + LangGraph + OpenAI APIs
- **Frontend**: React + Material-UI
- **Infrastructure**: Docker + Docker Compose
- **AI Services**: OpenAI GPT-4 + Whisper

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   OpenAI APIs   │
│                 │────│                 │────│                 │
│ • Audio Input   │    │ • LangGraph     │    │ • Whisper       │
│ • Text Input    │    │ • Validation    │    │ • GPT-4         │
│ • Results UI    │    │ • Error Handler │    │ • Structured    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 Processing Workflow

The application implements a **3-stage LangGraph workflow**:

1. **Audio Transcription Node**
   - Accepts audio file URLs and file uploads
   - Downloads and transcribes using OpenAI Whisper
   - Passes transcribed text to next stage

2. **Medical Information Extraction Node**
   - Processes text (from transcription or direct input)
   - Extracts structured data using GPT-4:
     - Patient information (name, age, ID, etc.)
     - List of symptoms
     - Consultation reason
   - Uses JSON schema for consistent output

3. **Diagnosis Generation Node**
   - Generates medical analysis based on extracted data:
     - Possible diagnosis
     - Treatment plan
     - Recommendations

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### 1. Clone and Setup
```bash
git clone https://github.com/pinkthepink/test_telepatia.git
cd test_telepatia
```

### 2. Configure Environment
```bash
# Copy the environment template
cp .env.example .env

# Edit the .env file and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Start the Application

#### Production Mode (Recommended)
```bash
# Build and start all services in production mode
docker-compose up --build -d

# Or run in foreground to see logs
docker-compose up --build
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📝 Usage Guide

### Audio Processing
1. Select the "Audio Input" tab
2. Choose between:
   - **Audio URL**: Paste a direct URL to an audio file
   - **File Upload**: Upload an audio file directly (MP3, WAV, M4A, etc.)
3. Click "Process Audio" or "Upload & Process"
4. View the transcription and medical analysis results

### Text Processing
1. Select the "Text Input" tab
2. Enter medical text (symptoms, consultation notes, etc.)
3. Click "Process Text"
4. View the extracted information and diagnosis

### Example Text Input
```
Patient John Smith, 45 years old, presents with severe headache for 3 days, 
accompanied by nausea and sensitivity to light. No fever. History of migraines 
in family. Seeking consultation for persistent symptoms.
```

## 🔍 API Endpoints

### Main Endpoints
- `POST /process` - Process audio URL or text
- `POST /process/upload` - Process uploaded audio file
- `GET /health` - Health check
- `GET /metrics` - Performance metrics
- `GET /workflow/status` - Workflow information

### Request Examples

**Audio Processing:**
```bash
curl -X POST "http://localhost:8000/process" \
-H "Content-Type: application/json" \
-d '{
  "audio_url": "https://example.com/medical-audio.mp3"
}'
```

**Text Processing:**
```bash
curl -X POST "http://localhost:8000/process" \
-H "Content-Type: application/json" \
-d '{
  "text": "Patient has severe headache and nausea for 3 days"
}'
```

## 🏗️ Project Structure

```
test_telepatia/
├── docker-compose.yml          # Docker orchestration
├── .env.example               # Environment template
├── README.md                   # This file
├── SETUP.md                   # Detailed setup guide
│
├── backend/                    # Python FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # FastAPI application
│       ├── graph/             # LangGraph workflow
│       │   ├── nodes.py       # Processing nodes
│       │   ├── workflow.py    # Workflow definition
│       │   └── schemas.py     # Data models
│       ├── middleware/        # Request/response middleware
│       ├── config/           # Configuration files
│       └── utils/            # Utility functions
│
└── frontend/                   # React frontend
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── App.js             # Main application
        ├── components/        # UI components
        │   ├── AudioInput.jsx
        │   ├── TextInput.jsx
        │   ├── ResultsDisplay.jsx
        │   └── ProcessingOverlay.jsx
        └── services/
            └── api.js         # API client
```

## ⚙️ Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Langfuse (for observability)
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_HOST=https://us.cloud.langfuse.com
```

### Supported Audio Formats
- MP3, WAV, M4A, AAC, OGG, FLAC
- Both direct URLs and file uploads supported
- Maximum file size: 25MB
- Maximum processing time: 180 seconds

## 🛡️ Security & Validation

### Backend Security Features
- Request validation middleware
- Input sanitization
- File type and size validation
- Error handling without sensitive data exposure
- CORS configuration for frontend integration

### Input Validation
- Audio URL format validation
- File type and size validation (25MB limit)
- Text length limits (10-10,000 characters)
- Malicious content filtering
- Request size limits

## 📊 Monitoring & Metrics

### Available Metrics
- Request counts and response times
- Processing costs (OpenAI API usage)
- System resource usage
- Error rates and types
- Workflow performance

### Observability
- **Langfuse Integration**: Full tracing of AI interactions
- Health checks and status endpoints
- Comprehensive logging and error tracking

## 🐛 Troubleshooting

### Common Issues

**"Backend API is not available"**
```bash
# Check if backend is running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Restart services
docker-compose restart
```

**File Upload Issues**
- Ensure file is under 25MB
- Check supported audio formats (MP3, WAV, M4A, AAC, OGG, FLAC)
- Verify backend has sufficient disk space for temporary files

**OpenAI API Errors**
- Verify API key is correctly set in `.env`
- Check OpenAI API quota and billing
- Ensure API key has access to GPT-4 and Whisper

### Debug Mode
```bash
# Run with verbose logging
docker-compose up --build

# View real-time logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## ⚠️ Important Disclaimers

**This application is for demonstration purposes only:**
- Not intended for actual medical diagnosis
- Results should not replace professional medical advice
- Always consult qualified healthcare professionals
- Educational and technical demonstration only

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and demonstration purposes.

## 🔗 External Dependencies

- **OpenAI API**: GPT-4 and Whisper models
- **LangGraph**: Workflow orchestration
- **FastAPI**: Python web framework
- **React**: Frontend framework
- **Material-UI**: UI component library
- **Docker**: Containerization
- **Langfuse**: LLM observability platform
