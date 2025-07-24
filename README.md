# Model Myself - Frontend & Backend Setup

This project contains a React frontend and FastAPI backend with hello world functionality.

## Project Structure

```
Model_Myself/
├── backend/
│   ├── main.py           # FastAPI backend
│   └── requirements.txt  # Python dependencies
├── src/
│   └── index.js          # React frontend application
├── public/
│   └── index.html        # HTML template
├── package.json          # Node.js dependencies
├── webpack.config.js     # Webpack configuration
└── README.md            # This file
```

## Setup Instructions

### Backend (FastAPI)

1. Navigate to backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend:
```bash
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend (React)

1. Install dependencies:
```bash
npm install
```

2. Start the frontend:
```bash
npm run
```

The frontend will be available at `http://localhost:3001`

## Features

- **Frontend**: React application with hello world message
- **Backend**: FastAPI server with `/hello` endpoint
- **Integration**: Frontend can call backend API and display response
- **Logging**: Comprehensive logging in both frontend (browser console) and backend (console + file)
- **CORS**: Properly configured to allow frontend-backend communication

## API Endpoints

- `GET /` - Root endpoint
- `GET /hello` - Returns JSON with "helo1234" message
- `GET /health` - Health check endpoint

## Usage

1. Start the backend server first
2. Start the frontend application
3. Click "Call Backend API" button to trigger the backend request
4. View the response and logs in both browser and backend console

## Logging

- **Frontend**: Logs displayed in browser console and on-screen
- **Backend**: Logs to console and `backend.log` file
- All requests and responses are logged with timestamps 