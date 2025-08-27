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
   - Accepts audio file URLs
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
git clone <repository-url>
cd teste_telepatia
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

#### Development Mode (For development)
```bash
# Run in development mode with hot reload
docker-compose -f docker-compose.dev.yml up --build -d
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🏭 Production vs Development

### Production Mode Features
- **Optimized React Build**: Minified, compressed assets
- **Nginx Serving**: Fast static file serving with gzip compression
- **Multi-stage Docker**: Smaller production images
- **Security Headers**: XSS protection, content type validation
- **Health Checks**: Container health monitoring

### Development Mode Features
- **Hot Reload**: Automatic refresh on code changes
- **Source Maps**: Better debugging experience
- **Volume Mounting**: Real-time code synchronization
- **Development Server**: React development server with better error messages

## 🔧 Manual Setup (Development)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY=your_api_key_here

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 📝 Usage Guide

### Audio Processing
1. Select the "Audio Input" tab
2. Paste a direct URL to an audio file (MP3, WAV, M4A, etc.)
3. Click "Process Audio"
4. View the transcription and medical analysis results

### Text Processing
1. Select the "Text Input" tab
2. Enter medical text (symptoms, consultation notes, etc.)
3. Click "Process Text"
4. View the extracted information and diagnosis

### Example Audio URLs for Testing
```
https://www.soundjay.com/misc/sounds/bell-ringing-05.wav
```

### Example Text Input
```
Patient John Smith, 45 years old, presents with severe headache for 3 days, 
accompanied by nausea and sensitivity to light. No fever. History of migraines 
in family. Seeking consultation for persistent symptoms.
```

## 🔍 API Endpoints

### Main Endpoints
- `POST /process` - Process audio URL or text
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
teste_telepatia/
├── docker-compose.yml          # Docker orchestration
├── .env                        # Environment variables
├── README.md                   # This file
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
│       │   ├── validation.py  # Input validation
│       │   ├── error_handler.py # Error handling
│       │   └── metrics.py     # Performance tracking
│       └── utils/
│           └── audio_downloader.py # Audio file handling
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
        │   └── LoadingIndicator.jsx
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
```

### Supported Audio Formats
- MP3, WAV, M4A, AAC, OGG, FLAC
- Direct URLs only (no file uploads)
- Maximum processing time: 60 seconds

## 🛡️ Security & Validation

### Backend Security Features
- Request validation middleware
- Input sanitization
- Rate limiting ready
- Error handling without sensitive data exposure
- CORS configuration for frontend integration

### Input Validation
- Audio URL format validation
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

### Health Checks
- Backend API health: `GET /health`
- OpenAI API connectivity
- Workflow status validation

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

**"Invalid audio URL format"**
- Ensure URL is publicly accessible
- Check that URL points to an actual audio file
- Verify supported audio format

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

## 🎯 Design Decisions

### LangGraph Implementation
- **Modular Nodes**: Each processing stage is an independent node
- **State Management**: Shared state across workflow stages
- **Error Handling**: Node-level and workflow-level error recovery
- **Async Processing**: Non-blocking audio downloads and API calls

### Frontend Architecture
- **Material-UI**: Consistent, professional medical UI
- **Tab-based Input**: Clear separation between audio and text input
- **Real-time Status**: Processing indicators and health monitoring
- **Responsive Design**: Works on desktop and mobile devices

### API Design
- **RESTful Endpoints**: Standard HTTP methods and status codes
- **Structured Responses**: Consistent JSON format with error details
- **Comprehensive Validation**: Input validation with clear error messages
- **Performance Monitoring**: Built-in metrics and logging

## 🔬 Medical Information Processing

### Extracted Data Structure
```json
{
  "symptoms": ["headache", "nausea", "sensitivity to light"],
  "patient_info": {
    "name": "John Smith",
    "age": 45,
    "identification_number": "12345",
    "gender": "male"
  },
  "consultation_reason": "Persistent headache symptoms",
  "diagnosis": "Possible migraine based on symptoms...",
  "treatment_plan": "Rest, hydration, pain medication...",
  "recommendations": "Follow up if symptoms persist..."
}
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

## 🆘 Support

For technical issues:
1. Check the troubleshooting section
2. Review application logs
3. Verify configuration settings
4. Check OpenAI API status

## 🔗 External Dependencies

- **OpenAI API**: GPT-4 and Whisper models
- **LangGraph**: Workflow orchestration
- **FastAPI**: Python web framework
- **React**: Frontend framework
- **Material-UI**: UI component library
- **Docker**: Containerization