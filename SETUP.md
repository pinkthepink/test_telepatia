# Medical Processing Application Setup Guide

This guide will help you set up the Medical Processing Application that uses OpenAI for transcription, medical extraction, and diagnosis generation, with Langfuse for observability.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed
- OpenAI API account and API key
- Langfuse account and project (for observability)

## 1. Get OpenAI API Key

1. **Visit OpenAI Platform**: Go to [https://platform.openai.com/](https://platform.openai.com/)

2. **Sign up or Log in**: Create an account or sign into your existing OpenAI account

3. **Navigate to API Keys**: 
   - Click on your profile in the top right
   - Select "View API keys" or go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

4. **Create New API Key**:
   - Click "Create new secret key"
   - Give it a descriptive name like "Medical Processing App"
   - Copy the key immediately (you won't be able to see it again)
   - **Important**: Keep this key secure and never commit it to version control

5. **Add Billing Information**: Ensure you have billing set up to use the API

## 2. Set up Langfuse Project

1. **Visit Langfuse**: Go to [https://langfuse.com/](https://langfuse.com/)

2. **Sign up**: Create a free account

3. **Create a Project**:
   - After signing up, you'll be prompted to create your first project
   - Name it something like "Medical Processing App"
   - Choose the appropriate region (US or EU)

4. **Get Project Keys**:
   - In your project dashboard, go to "Settings" → "API Keys"
   - Copy your:
     - **Public Key** (starts with `pk-lf-`)
     - **Secret Key** (starts with `sk-lf-`)
   - Note your **Host URL**:
     - US: `https://us.cloud.langfuse.com`
     - EU: `https://cloud.langfuse.com`

## 3. Configure Environment Variables

1. **Clone the Repository** (if you haven't already):
   ```bash
   git clone <your-repository-url>
   cd teste_telepatia
   ```

2. **Copy Environment File**:
   ```bash
   # Copy the example file
   cp .env.example .env
   ```

3. **Edit the .env file** with your actual values:
   ```bash
   # OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here

   # Server Configuration
   BACKEND_PORT=8000
   FRONTEND_PORT=3000

   # Langfuse Configuration
   LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
   LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
   LANGFUSE_HOST=https://us.cloud.langfuse.com
   ```

   **Replace the placeholder values**:
   - `your_openai_api_key_here` → Your actual OpenAI API key (starts with `sk-`)
   - `your_langfuse_secret_key_here` → Your Langfuse secret key (starts with `sk-lf-`)
   - `your_langfuse_public_key_here` → Your Langfuse public key (starts with `pk-lf-`)
   - Update `LANGFUSE_HOST` if you're using EU region

## 4. Deploy the Application

1. **Build and Start the Application**:
   ```bash
   docker-compose up --build -d
   ```

2. **Verify Containers are Running**:
   ```bash
   docker ps
   ```
   You should see both `teste_telepatia-backend-1` and `teste_telepatia-frontend-1` running.

3. **Check Logs** (if needed):
   ```bash
   # Backend logs
   docker logs teste_telepatia-backend-1

   # Frontend logs
   docker logs teste_telepatia-frontend-1
   ```

## 5. Test the Application

1. **Open the Frontend**: Navigate to [http://localhost:3000](http://localhost:3000)

2. **Test with Sample Text**:
   - Enter some medical text like: "Patient reports headache and fever for 2 days"
   - Click "Process Medical Information"
   - Wait for the results (takes 8-12 seconds due to AI processing)

3. **API Testing** (optional):
   ```bash
   curl -X POST "http://localhost:8000/process" \
     -H "Content-Type: application/json" \
     -d '{"text": "Patient reports headache and fever for 2 days", "audio_url": null}'
   ```

4. **Check Langfuse Dashboard**:
   - Go to your Langfuse project dashboard
   - You should see traces appearing for each medical processing request
   - Look for traces named `medical_workflow` with nested spans for each processing step

## 6. Application Features

- **Text Input**: Process medical text directly
- **Audio Input**: Upload audio files for transcription (uses OpenAI Whisper)
- **Medical Extraction**: Extracts symptoms, patient info, and consultation reason
- **Diagnosis Generation**: Provides possible diagnosis, treatment plan, and recommendations
- **Observability**: Full tracing of AI interactions via Langfuse

## Troubleshooting

### Common Issues

1. **"Invalid OpenAI API Key" Error**:
   - Verify your API key is correct in the `.env` file
   - Ensure you have billing set up in your OpenAI account
   - Check that your API key has not been revoked

2. **Langfuse Authentication Errors**:
   - Verify your Langfuse keys are correct in the `.env` file
   - Ensure the `LANGFUSE_HOST` matches your region
   - Check that your Langfuse project is active

3. **Containers Not Starting**:
   - Run `docker-compose logs` to see detailed error messages
   - Ensure ports 3000 and 8000 are not in use by other applications
   - Try rebuilding: `docker-compose down && docker-compose up --build`

4. **Frontend Shows "Backend API not available"**:
   - Check that the backend container is running: `docker ps`
   - Verify backend health: `curl http://localhost:8000/health`
   - Check backend logs: `docker logs teste_telepatia-backend-1`

### Getting Help

- Check the application logs using `docker logs <container-name>`
- Ensure all environment variables are properly set in the `.env` file
- Verify that Docker and Docker Compose are properly installed and running

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and rotate them regularly
- The `.env` file is already included in `.gitignore` to prevent accidental commits
- Consider using environment-specific `.env` files for different deployments

## Optional: Development Mode

If you want to run the application in development mode:

1. The frontend supports hot reloading during development
2. Backend logs are more verbose in development mode
3. You can modify the `NODE_ENV` and `FASTAPI_ENV` variables in the docker-compose.yml

---

**🎉 Congratulations!** Your Medical Processing Application should now be running successfully with full AI-powered medical text analysis and observability tracking.