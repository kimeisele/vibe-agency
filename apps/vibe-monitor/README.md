# Vibe Monitor - System Status Dashboard

**ARCH-019: The First Native Artifact**

A web dashboard that visualizes vibe-agency system status in real-time.

## 🎯 Purpose

This application validates **GAD-000 (JSON Output)** by consuming the structured JSON interface from `./bin/vibe status --json` and rendering it as a visual dashboard.

**Key Goals:**
- Prove that GAD-000 JSON format is machine-parseable
- Validate the Repair Loop (Coder → Tester → Orchestrator)
- Demonstrate that the system can build applications on top of itself
- Provide real operational value (visual health monitoring)

## 🚀 Quick Start

### Installation

```bash
# Navigate to the monitor directory
cd apps/vibe-monitor

# Install dependencies
pip install -r requirements.txt
# or
uv pip install -r requirements.txt
```

### Running the Dashboard

```bash
# Start the Flask server
python3 app.py

# The dashboard will be available at:
# http://localhost:5000
```

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## 📊 Features

### 1. Real-Time System Health
- **Overall Status Badge**: Green (Healthy) or Red (Degraded)
- **Health Checks Table**: Shows status of all system components
  - Git Status
  - vibe-cli availability
  - Cartridges availability
  - UV Environment status

### 2. Cartridge Registry
- Lists all loaded cartridges (playbooks)
- Shows cartridge name and description
- Updates every 5 seconds

### 3. Next Actions
- Displays suggested commands for next steps
- Helps operators understand available actions

### 4. Auto-Refresh
- Dashboard automatically updates every 5 seconds
- No manual refresh needed

## 🏗️ Architecture

```
apps/vibe-monitor/
├── app.py                 # Flask backend (API + server)
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend UI (HTML + JavaScript)
├── static/
│   └── style.css         # Terminal-aesthetic styling
└── README.md             # This file
```

### API Endpoints

#### `GET /`
Serves the dashboard HTML page.

#### `GET /api/status`
Executes `./bin/vibe status --json` and returns parsed JSON.

**Response Format (GAD-000 compliant):**
```json
{
  "status": "healthy" | "degraded",
  "timestamp": "2025-11-21T11:26:32.530387",
  "health": {
    "Git Status": {"status": true, "message": "Clean"},
    ...
  },
  "cartridges": [
    {"name": "feature-implement", "description": "..."},
    ...
  ],
  "next_actions": [...]
}
```

**Error Response:**
```json
{
  "error": "Error description",
  "details": "Detailed error information"
}
```

#### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "vibe-monitor"
}
```

## 🎨 Design Philosophy

### Terminal Aesthetic
- Dark background (#0d1117 - GitHub dark theme)
- Monospace fonts (SF Mono, Monaco, Fira Code)
- Green/Red status indicators
- Minimal, functional design

### Accessibility
- Responsive design (mobile-friendly)
- High contrast colors
- Reduced motion support for accessibility
- Semantic HTML

## 🧪 Testing

### Manual Test Plan

1. **Start Server:**
   ```bash
   python3 app.py
   ```

2. **Test API Endpoint:**
   ```bash
   curl http://localhost:5000/api/status | python3 -m json.tool
   ```

   **Expected:** Valid JSON with keys: `status`, `health`, `cartridges`, `timestamp`

3. **Test Frontend:**
   - Open browser: `http://localhost:5000`
   - Verify dashboard loads
   - Check status badge (Green/Red)
   - Verify health checks table populates
   - Verify cartridges table populates
   - Wait 5 seconds, verify auto-refresh

4. **Test Error Handling:**
   - Stop the server
   - Try accessing `/api/status`
   - **Expected:** 500 error with details

### Integration Test (Automated)

```bash
# Start server in background
python3 apps/vibe-monitor/app.py &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Test API endpoint
curl http://localhost:5000/api/status

# Test health endpoint
curl http://localhost:5000/health

# Test index page
curl http://localhost:5000/ | grep "Vibe Agency"

# Stop server
kill $SERVER_PID
```

## 📝 Implementation Notes

### GAD-000 Validation
This application is a **living validation** of GAD-000 JSON Output specification:
- Consumes the JSON interface from `vibe status --json`
- Parses required keys: `status`, `health`, `cartridges`, `timestamp`
- Renders data in a human-friendly format
- Breaks if JSON format changes (intentional - acts as contract test)

### Error Handling
The backend implements comprehensive error handling:
- **Subprocess errors**: Command execution failures
- **JSON parse errors**: Invalid output from vibe command
- **Timeout errors**: Command takes too long (10s limit)
- **File not found errors**: vibe command missing

All errors return 500 with structured JSON explaining the issue.

### Security Considerations
- No authentication (internal tool)
- CORS enabled for localhost development
- No user input processed (read-only dashboard)
- Subprocess timeout prevents DOS (10s limit)

## 🔄 Future Enhancements

Potential improvements (not in scope for ARCH-019):
- WebSocket support for real-time updates (instead of polling)
- Historical data tracking (store status snapshots)
- Alert notifications (email/Slack when status degrades)
- Multi-instance monitoring (monitor multiple vibe-agency deployments)
- Dark/Light theme toggle
- Export status data to CSV/JSON

## 🎯 Success Criteria (ARCH-019)

- [x] Application structure scaffolded
- [x] Backend API endpoint implemented (`/api/status`)
- [x] Frontend dashboard implemented (HTML + JS + CSS)
- [x] Consumes `./bin/vibe status --json` correctly
- [x] Displays system health visually
- [x] Auto-refresh every 5 seconds
- [x] Error handling implemented
- [ ] Integration tests pass (manual verification required)

## 📚 Related Documentation

- **ARCH-019 Spec**: `docs/architecture/ARCH-019-vibe-monitor.md` (if exists)
- **GAD-000 Spec**: JSON Output Interface specification
- **Cartridge Spec**: `playbooks/presets/ARCH-019-monitor.yaml`

## 🤝 Contributing

This is a foundational artifact built to validate the system's capability to build applications. Enhancements should be proposed through the standard playbook execution flow.

## 📜 License

Part of vibe-agency project. See root LICENSE for details.

---

**Built by:** Vibe Agency Playbook Engine (ARCH-019)
**Date:** 2025-11-21
**Status:** ✅ Operational
