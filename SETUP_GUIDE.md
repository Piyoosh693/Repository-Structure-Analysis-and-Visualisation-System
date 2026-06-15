# Setup & Integration Guide

This document explains how to set up and configure the Codebase Analyzer application with both frontend and backend.

## Prerequisites

- **Backend**: Python 3.8+
- **Frontend**: Node.js 16+
- **Gemini API Key**: Required for AI summaries (get one from Google AI Studio)

---

## Backend Setup

### 1. Install Dependencies

```bash
cd backend/backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example configuration and add your API key:

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

**Environment Variables:**
- `GEMINI_API_KEY` *(required)*: Your Gemini API key
- `GEMINI_MODEL` *(optional)*: Gemini model for summaries
  - Default: `gemini-2.5-flash`
- `CORS_ORIGINS` *(optional)*: Comma-separated list of allowed frontend origins
  - Default: `http://localhost:5173,http://localhost:3000` (for development)
  - Production example: `https://app.example.com`

### 3. Run the Backend Server

```bash
# From backend/backend directory
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL (Optional)

The frontend defaults to same-origin `/api` requests for local development. Vite proxies those requests to `http://localhost:8000`.

For custom setups or production:

```bash
# Copy example configuration
cp .env.example .env

# Edit .env to set your backend URL if you are not using the Vite dev proxy
# VITE_API_URL=https://api.example.com
```

### 3. Run the Development Server

```bash
npm run dev
```

The frontend will run at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

---

## API Integration

### POST /api/graph — Analyze a Repository

**Request:**
```json
{
  "path": "/absolute/path/to/repo"
}
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "src/utils/parser.py",
      "path": "src/utils/parser.py",
      "label": "parser.py",
      "language": "python",
      "loc": 150,
      "total_lines": 200,
      "blank_lines": 20,
      "comment_lines": 30,
      "complexity": 5.2,
      "size_kb": 12.5
    }
  ],
  "edges": [
    {
      "id": "src/main.py->src/utils/parser.py",
      "source": "src/main.py",
      "target": "src/utils/parser.py"
    }
  ],
  "meta": {
    "file_count": 42,
    "edge_count": 120,
    "languages": { "python": 35, "javascript": 7 },
    "total_loc": 5250
  }
}
```

### POST /api/summarize — Get AI Summary

**Request:**
```json
{
  "filepath": "src/utils/parser.py",
  "repo_root": "/absolute/path/to/repo",
  "language": "python",
  "content_hash": "optional_sha256_hash"
}
```

**Response:**
```json
{
  "summary": "This module parses Python source code...",
  "cached": false,
  "content_hash": "abc123def456..."
}
```

### GET /api/health — Health Check

**Response:**
```json
{
  "status": "ok"
}
```

---

## Troubleshooting

### Frontend can't connect to backend

**Error:** `Cannot connect to API server at http://localhost:8000`

**Solutions:**
1. Ensure backend is running: `python -m uvicorn app.main:app --reload --port 8000`
2. Check CORS configuration in `backend/app/main.py`
3. Verify `VITE_API_URL` matches your backend URL

### API returns 405 Method Not Allowed

**Cause:** Frontend is using wrong HTTP method

**Fix:** Ensure frontend uses POST for `/api/graph` endpoint (not GET)

### Summarization fails with "Missing API key"

**Error:** `RuntimeError: GEMINI_API_KEY environment variable is not set`

**Solutions:**
1. Add `GEMINI_API_KEY` to `backend/backend/.env`
2. Restart the backend server
3. Verify the key is valid in Google AI Studio

### CORS errors in browser console

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solutions:**
1. Update `CORS_ORIGINS` in `backend/.env` to include your frontend URL
2. Restart backend server
3. Verify frontend URL format: `http://localhost:5173` (not `localhost:5173`)

---

## Development Workflow

1. **Start Backend:** `cd backend/backend && python -m uvicorn app.main:app --reload --port 8000`
2. **Start Frontend:** `cd frontend && npm run dev`
3. **Open Browser:** http://localhost:5173
4. **API Docs:** http://localhost:8000/docs

---

## Production Deployment

### Backend

```bash
# Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

# Or with Uvicorn directly
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Set environment variables:
- `CORS_ORIGINS=https://your-frontend-domain.com`
- `GEMINI_API_KEY=your-production-key`
- `GEMINI_MODEL=gemini-2.5-flash`

### Frontend

```bash
# Build optimized bundle
npm run build

# Preview production build locally
npm run preview

# Deploy `dist/` folder to your web server
```

Update `VITE_API_URL` before building:
```bash
VITE_API_URL=https://your-api-domain.com npm run build
```

---

## Project Structure

```
backend/
  backend/
    app/
      api/
        models.py          # Pydantic request/response models
        routes.py          # API endpoints
      core/
        graph_builder.py   # Graph construction logic
        parser.py          # Code parsing
        metrics.py         # Complexity calculation
      services/
        ai_service.py      # Gemini AI integration
        cache_service.py    # Summary caching
    main.py               # FastAPI app setup & CORS

frontend/
  src/
    hooks/
      useGraphData.js     # Graph fetching hook
      useSummary.js       # Summary fetching hook
    utils/
      apiClient.js        # Axios API client (NEW)
      layoutEngine.js     # Graph layout algorithm
    components/
      GraphCanvas.jsx     # ReactFlow visualization
      SidePanel.jsx       # File summary display
```

---

## API Changes Summary

### v1.0.0 Updates

1. **POST /api/graph** — Changed from GET query parameter to POST body
   - Before: `GET /api/graph?path=/repo/path`
   - After: `POST /api/graph` with body `{ "path": "/repo/path" }`

2. **POST /api/summarize** — Now requires all fields for proper file lookup
   - Required: `filepath`, `repo_root`, `language`
   - Optional: `content_hash` (computed by backend if omitted)

3. **Node Response** — Added `path` field for frontend convenience
   - Both `id` and `path` contain the relative file path

4. **CORS Configuration** — Environment variable support
   - Configurable via `CORS_ORIGINS` environment variable
   - Supports production domain deployment

---

## Support

For issues or questions:
1. Check API docs at `http://localhost:8000/docs`
2. Review error messages in browser console
3. Check backend logs for detailed errors
4. Verify all environment variables are set correctly
