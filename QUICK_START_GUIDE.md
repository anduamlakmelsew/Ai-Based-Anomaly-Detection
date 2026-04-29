# Quick Start Guide - AI Security Scanner

## 🚀 Start the System

### Backend
```bash
cd backend
source venv/bin/activate
python run.py
```
✅ Backend runs on: **http://127.0.0.1:5002**

### Frontend
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend runs on: **http://localhost:5173**

## 🔐 Default Credentials
- **Username:** `admin`
- **Password:** `admin123`

## 🧪 Test the System

### 1. Check Backend Health
```bash
curl http://127.0.0.1:5002/ping
```
Expected: `{"message": "pong"}`

### 2. Test Login
```bash
curl -X POST http://127.0.0.1:5002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```
Expected: `{"access_token": "...", "user": {...}}`

### 3. Test Scan Endpoint
```bash
# Get token from login response, then:
curl -X POST http://127.0.0.1:5002/api/scan/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"target":"127.0.0.1","scan_type":"network","sync":true}'
```

## ✅ Verification Checklist

### Backend
- [ ] Server starts without errors
- [ ] Port 5002 is accessible
- [ ] Database seeded successfully
- [ ] WebSocket server initialized
- [ ] `/ping` endpoint responds

### Frontend
- [ ] Application loads in browser
- [ ] Login page displays
- [ ] Can login with admin credentials
- [ ] Dashboard loads without errors
- [ ] Console shows: `✅ WebSocket connected`
- [ ] No red errors in browser console

### Integration
- [ ] API calls succeed (check Network tab)
- [ ] WebSocket connects (check Console)
- [ ] Dashboard displays data
- [ ] Can start a scan
- [ ] Scan results appear

## 🐛 Troubleshooting

### Backend won't start
**Problem:** Port already in use
**Solution:** 
```bash
# Kill process on port 5002
lsof -ti:5002 | xargs kill -9
# Or use a different port in backend/run.py
```

### Frontend can't connect
**Problem:** Wrong API URL
**Solution:** Check `frontend/src/services/api.js` has:
```javascript
baseURL: "http://127.0.0.1:5002/api"
```

### WebSocket not connecting
**Problem:** Port mismatch
**Solution:** All Socket.IO connections should use:
```javascript
io("http://127.0.0.1:5002", {...})
```

### 401 Unauthorized errors
**Problem:** Token expired or invalid
**Solution:** Logout and login again

## 📊 Expected Console Output

### Backend
```
Server initialized for threading.
✅ Database seeded successfully
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5002
[INFO] Client connected
Upgrade to websocket successful
```

### Frontend
```
✅ WebSocket connected
📊 Loading dashboard data...
✅ Dashboard stats loaded
✅ Loaded X scans from history
```

## 🎯 Key Features

### Available Scan Types
1. **Network Scan** - Port scanning and service detection
2. **Web Scan** - Web application security testing
3. **System Scan** - System configuration analysis

### Dashboard Features
- Real-time scan progress
- Risk score visualization
- Vulnerability statistics
- Activity logs
- AI-powered threat detection

### API Endpoints
- `POST /api/auth/login` - Authentication
- `POST /api/scan/start` - Start scan
- `GET /api/scan/history` - Scan history
- `GET /api/scan/{id}` - Scan details
- `GET /api/dashboard/stats` - Dashboard stats

## 📁 Project Structure

```
AI_Baseline_Assessment_Scanner/
├── backend/
│   ├── app/
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── models/      # Database models
│   │   ├── scanner/     # Scanning modules
│   │   └── ai/          # AI analysis
│   ├── run.py           # Entry point
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── pages/       # React pages
    │   ├── services/    # API services
    │   ├── components/  # React components
    │   └── config/      # Configuration
    ├── package.json
    └── vite.config.js
```

## 🔧 Configuration Files

### Backend
- `backend/.env` - Environment variables
- `backend/run.py` - Server configuration
- `backend/app/__init__.py` - App initialization

### Frontend
- `frontend/src/services/api.js` - API base URL
- `frontend/src/config/api.config.js` - Centralized config
- `frontend/vite.config.js` - Vite configuration

## 📚 Documentation

- `backend/STABILIZATION_REPORT.md` - Backend fixes
- `frontend/WEBSOCKET_FIX_REPORT.md` - Frontend fixes
- `FRONTEND_BACKEND_FIX_SUMMARY.md` - Complete summary
- `QUICK_START_GUIDE.md` - This file

## 🎉 Success Indicators

✅ Backend running on port 5002
✅ Frontend running on port 5173
✅ WebSocket connected
✅ Dashboard loads without errors
✅ Can login and start scans
✅ Real-time updates working

---
*Last Updated: 2026-04-29*
*Status: FULLY OPERATIONAL* ✅
