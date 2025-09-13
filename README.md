# GxP Compliance Assistant

A comprehensive document compliance checking system for GxP regulations using AI-powered analysis.

## Features

- **Multi-format Support**: Analyze both PDF and DOCX documents
- **AI-Powered Analysis**: Uses Azure OpenAI for intelligent compliance checking
- **Real-time Processing**: Get immediate compliance scores and findings
- **Modern Web Interface**: React-based frontend with real-time updates
- **Comprehensive Reporting**: Detailed compliance findings with severity levels

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Azure OpenAI**: Chat and embedding models for AI analysis
- **ChromaDB**: Vector database for document storage and retrieval
- **PyPDF**: PDF document parsing
- **python-docx**: DOCX document parsing

### Frontend
- **React 19**: Modern React with Vite
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons

## Setup Instructions

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- Azure OpenAI API access

### 1. Environment Configuration

The `.env` file in the backend directory contains all the Azure OpenAI configuration:

```env
# Azure OpenAI Embedding
AZURE_OPENAI_EMBEDDING_API_KEY=your_embedding_api_key
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment_name
AZURE_OPENAI_EMBEDDING_API_VERSION=2024-02-01

# Azure OpenAI Chat
AZURE_OPENAI_CHAT_API_KEY=your_chat_api_key
AZURE_OPENAI_CHAT_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment_name
AZURE_OPENAI_CHAT_API_VERSION=2024-02-01
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirement.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Running the Application

#### Option 1: Use Start Scripts (Recommended)

**Windows Batch File:**
```bash
start.bat
```

**PowerShell:**
```powershell
.\start.ps1
```

#### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs

## API Endpoints

- `GET /` - API health check
- `GET /health` - Detailed health status
- `GET /api/config` - Configuration status
- `POST /analyze-sop/` - Upload and analyze documents

## Usage

1. Open the frontend at http://localhost:5173
2. Upload PDF or DOCX documents using the drag-and-drop interface
3. Wait for analysis to complete
4. Review compliance scores and detailed findings
5. View aggregate statistics across all uploaded documents

## Document Analysis

The system performs comprehensive analysis including:

- **Section Validation**: Checks for mandatory sections like Purpose, Scope, Responsibilities
- **Content Quality**: Identifies placeholders and incomplete content
- **Reference Checking**: Validates document references and citations
- **Compliance Scoring**: Provides 0-100 compliance scores based on findings
- **Severity Classification**: Categorizes issues as Critical, Major, or Minor

## Configuration

All configuration is centralized in `backend/config/config.py` and reads from environment variables. The system validates configuration on startup and provides clear error messages for missing required settings.

## Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   React Frontend│ ───────────────▶│  FastAPI Backend│
│   (Port 5173)   │                 │   (Port 8000)   │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │  Azure OpenAI   │
                                    │ Chat + Embeddings│
                                    └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │   ChromaDB      │
                                    │ Vector Database │
                                    └─────────────────┘
```

## Troubleshooting

### Backend Issues
- Ensure all Python dependencies are installed
- Check that Azure OpenAI credentials are correctly set in `.env`
- Verify the backend is running on port 8000

### Frontend Issues  
- Ensure Node.js dependencies are installed (`npm install`)
- Check that the backend is accessible from the frontend
- Verify Vite proxy configuration in `vite.config.js`

### API Connection Issues
- Check if both servers are running
- Verify the proxy configuration in Vite
- Check browser console for CORS errors

## Development

The project uses modern development practices:

- **Hot Reload**: Both frontend and backend support hot reloading
- **Type Safety**: TypeScript-ready React components
- **Error Handling**: Comprehensive error handling on both ends
- **Logging**: Detailed logging for debugging
- **Validation**: Input validation and sanitization

## License

This project is part of a hackathon and is for demonstration purposes.
