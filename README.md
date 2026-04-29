# AI-Based Anomaly Detection & Security Scanner

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/React-19-blue.svg" alt="React 19">
  <img src="https://img.shields.io/badge/Flask-3.1-green.svg" alt="Flask 3.1">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/AI-RandomForest-orange.svg" alt="AI: RandomForest">
</p>

A comprehensive AI-powered security assessment platform that performs network scanning, web vulnerability detection, and system security auditing with real-time anomaly detection using machine learning.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Database Migrations](#database-migrations)
- [AI Model Management](#ai-model-management)
- [Logging](#logging)
- [Data Export](#data-export)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

### 🔍 Security Scanning
- **Network Scanning**: Port scanning, service detection, OS fingerprinting
- **Web Vulnerability Scanning**: OWASP Top 10 checks, injection testing, security headers
- **System Security Auditing**: Configuration compliance, security baseline checks

### 🤖 AI-Powered Anomaly Detection
- **Multi-Domain ML Models**: Trained RandomForest models for network, web, and system analysis
- **Real-time Analysis**: AI runs on every scan to detect anomalies
- **Confidence Scoring**: Probability-based predictions with confidence metrics
- **Model Versioning**: Track and manage multiple model versions

### 📊 Real-Time Dashboard
- **Live Scan Updates**: WebSocket-based real-time progress tracking
- **Risk Assessment**: Dynamic risk scoring with visual indicators
- **Activity Logging**: Complete audit trail of all security activities
- **AI Insights Panel**: View anomaly predictions and recommendations

### 📄 Reporting & Export
- **PDF Reports**: Generate comprehensive security assessment reports
- **Data Export**: CSV, JSON export capabilities
- **Historical Analysis**: Track security posture over time

### 🔐 Authentication & Authorization
- **JWT-Based Authentication**: Secure token-based access
- **Role-Based Access Control**: Admin, Analyst, and Viewer roles
- **Audit Logging**: Complete user activity tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 19)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │  Dashboard  │ │   Scanner   │ │   Reports   │ │   Settings  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP/WebSocket
┌──────────────────────────────▼──────────────────────────────────┐
│                     BACKEND (Flask 3.1)                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    API Layer (REST)                       │ │
│  │  /api/auth  /api/scan  /api/dashboard  /api/reports        │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                   │
│  ┌──────────────────────────▼─────────────────────────────────┐│
│  │              Services Layer                                 ││
│  │  ScanService │ AlertService │ ReportService │ AIService    ││
│  └──────────────────────────┬─────────────────────────────────┘│
│                             │                                  │
│  ┌──────────────────────────▼─────────────────────────────────┐│
│  │              AI/ML Pipeline (scikit-learn)                ││
│  │  Network Model │ Web Model │ System Model │ Anomaly Detect││
│  └──────────────────────────┬─────────────────────────────────┘│
│                             │                                  │
│  ┌──────────────────────────▼─────────────────────────────────┐│
│  │              Scanner Modules                              ││
│  │  Network Scanner │ Web Scanner │ System Scanner          ││
│  └───────────────────────────────────────────────────────────┘│
└──────────────────────────────┬──────────────────────────────────┘
                               │ SQLAlchemy
┌──────────────────────────────▼──────────────────────────────────┐
│                    DATABASE (SQLite/PostgreSQL)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Users   │ │  Scans   │ │  Alerts  │ │Anomalies │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **Git**: For cloning the repository

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI_Baseline_Assessment_Scanner
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=sqlite:///instance/ai_baseline.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/ai_baseline

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600

# AI Model Path
AI_MODEL_PATH=app/ai/models

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# File Upload
MAX_UPLOAD_SIZE=100MB
UPLOAD_FOLDER=uploads/models
```

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_SOCKET_URL=http://localhost:5000
```

### Database Initialization

The database will be automatically created when you first run the application. To initialize with seed data:

```bash
cd backend
python -c "from app import create_app; create_app()"
```

## Running the Application

### Development Mode

#### Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```
The backend will start on `http://localhost:5000`

#### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```
The frontend will start on `http://localhost:5173`

### Production Mode

#### Backend:
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

#### Frontend:
```bash
cd frontend
npm run build
# Serve the dist/ folder with your web server (nginx, Apache, etc.)
```

## API Documentation

### Swagger UI

Once the backend is running, access the interactive API documentation at:

```
http://localhost:5000/api/docs
```

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout user

#### Scanning
- `POST /api/scan/start` - Start a new scan
- `GET /api/scan/history` - Get scan history
- `GET /api/scan/<id>` - Get specific scan details
- `POST /api/scan/discover` - Network discovery

#### Dashboard
- `GET /api/dashboard/stats` - Get comprehensive dashboard stats
- `GET /api/dashboard/summary` - Get quick summary
- `GET /api/dashboard/activity` - Get activity feed
- `GET /api/dashboard/ai-insights` - Get AI insights

#### Reports
- `GET /api/reports/export/<format>` - Export data (csv, json, pdf)
- `POST /api/reports/generate` - Generate PDF report

#### Model Management
- `POST /api/models/upload` - Upload new AI model
- `GET /api/models` - List all models
- `GET /api/models/<id>/activate` - Activate specific model version

## Testing

### Running Tests

```bash
# Backend tests
cd backend
pytest

# With coverage
cd backend
pytest --cov=app tests/

# Frontend tests
cd frontend
npm test
```

### Test Structure

```
tests/
├── backend/
│   ├── test_auth.py
│   ├── test_scan.py
│   ├── test_dashboard.py
│   └── test_ai_pipeline.py
└── frontend/
    └── component_tests/
```

## Database Migrations

### Using Alembic

```bash
cd backend

# Create a new migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback one revision
flask db downgrade

# View current revision
flask db current

# View migration history
flask db history
```

## AI Model Management

### Model Structure

Models are stored in `backend/app/ai/models/`:

```
ai/models/
├── network_model.pkl
├── web_model.pkl
├── web_vectorizer.pkl
├── system/
│   └── system_model.pkl
└── versions/
    ├── network_model_v1.0.0.pkl
    ├── network_model_v1.1.0.pkl
    └── manifest.json
```

### Uploading New Models

Use the API to upload new trained models:

```bash
curl -X POST http://localhost:5000/api/models/upload \
  -H "Authorization: Bearer <jwt_token>" \
  -F "model=@new_network_model.pkl" \
  -F "model_type=network" \
  -F "version=2.0.0" \
  -F "description=Improved accuracy with new features"
```

### Model Versioning

Each model has:
- **Version**: Semantic versioning (e.g., 1.2.0)
- **Type**: network, web, or system
- **Created At**: Timestamp
- **Accuracy**: Model performance metric
- **Status**: active, deprecated, or archived

## Logging

### Log Configuration

Logs are stored in `backend/logs/`:

- `app.log` - Application logs
- `scan.log` - Scan activity logs
- `ai.log` - AI prediction logs
- `auth.log` - Authentication logs

### Log Levels

Set via environment variable `LOG_LEVEL`:
- `DEBUG` - Detailed debugging info
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical issues

### Viewing Logs

```bash
# View live logs
tail -f backend/logs/app.log

# View scan logs
cat backend/logs/scan.log | grep "ERROR"
```

## Data Export

### Supported Formats

- **CSV**: Spreadsheet format for analysis
- **JSON**: Machine-readable format
- **PDF**: Professional security reports

### Export API

```bash
# Export scans to CSV
curl http://localhost:5000/api/reports/export/csv \
  -H "Authorization: Bearer <jwt_token>" \
  -o scans_export.csv

# Generate PDF report
curl -X POST http://localhost:5000/api/reports/generate \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"scan_ids": [1, 2, 3], "format": "pdf"}' \
  -o report.pdf
```

## Project Structure

```
AI_Baseline_Assessment_Scanner/
├── README.md
├── requirements.txt
├── setup_admin.py              # Admin user setup script
│
├── backend/
│   ├── app/
│   │   ├── __init__.py         # Flask app factory
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # Database setup
│   │   ├── socket_events.py    # WebSocket handlers
│   │   │
│   │   ├── ai/                 # AI/ML components
│   │   │   ├── models/         # Trained model files
│   │   │   ├── training/       # Training scripts
│   │   │   ├── pipeline.py     # Unified AI interface
│   │   │   ├── network_pipeline.py
│   │   │   ├── web_pipeline.py
│   │   │   └── system_pipeline.py
│   │   │
│   │   ├── models/             # SQLAlchemy models
│   │   │   ├── scan_model.py
│   │   │   ├── user_model.py
│   │   │   └── alert_model.py
│   │   │
│   │   ├── routes/             # API endpoints
│   │   │   ├── auth_routes.py
│   │   │   ├── scan_routes.py
│   │   │   └── dashboard_routes.py
│   │   │
│   │   ├── scanner/            # Scanning engines
│   │   │   ├── network/        # Network scanner
│   │   │   ├── web/            # Web vulnerability scanner
│   │   │   └── system/         # System security scanner
│   │   │
│   │   ├── services/           # Business logic
│   │   │   ├── scan_service.py
│   │   │   └── alert_service.py
│   │   │
│   │   └── utils/              # Utilities
│   │       ├── audit_logger.py
│   │       └── db_seed.py
│   │
│   ├── migrations/             # Alembic migrations
│   ├── logs/                   # Application logs
│   ├── uploads/                # File uploads
│   ├── instance/               # Database files
│   └── tests/                  # Unit tests
│
├── frontend/
│   ├── src/
│   │   ├── pages/              # React pages
│   │   │   ├── Dashboard/
│   │   │   ├── Scanner/
│   │   │   └── Auth/
│   │   │
│   │   ├── components/         # React components
│   │   ├── services/           # API services
│   │   └── utils/              # Frontend utilities
│   │
│   ├── public/                 # Static assets
│   └── tests/                  # Frontend tests
│
└── docs/                       # Additional documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8
- **JavaScript**: Follow Airbnb Style Guide
- **Commit Messages**: Use conventional commits

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@example.com or join our Slack channel.

## Acknowledgments

- OWASP Foundation for security guidelines
- scikit-learn for machine learning capabilities
- Flask and React communities for excellent frameworks
