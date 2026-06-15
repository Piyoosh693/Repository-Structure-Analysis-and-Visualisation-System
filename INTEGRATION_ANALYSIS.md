# Frontend-Backend Integration Analysis

## Overview
The frontend (React/Vite) and backend (FastAPI) have **CRITICAL MISMATCHES** that will cause runtime failures. Below are the issues and required fixes.

---

## 🔴 CRITICAL ISSUES

### 1. **API Endpoint Mismatch: POST vs GET for /api/graph**
**Severity:** CRITICAL — App will crash on graph fetch

#### Problem:
- **Frontend** (`useGraphData.js` line 15): Uses `axios.post('/api/graph', { path: repoPath })`
- **Backend** (`routes.py` line 35): Expects `GET /api/graph?path=<repo_path>`

#### Impact:
Graph fetching will fail with a 405 Method Not Allowed error.

#### Fix Required:
**Change backend route from GET to POST:**

```python
@router.post("/graph", response_model=GraphResponse, tags=["analysis"])
def get_graph(body: dict):
    path = body.get("path")
    # ... rest of implementation
```

OR change frontend to use GET (less intuitive for an analysis endpoint).

---

### 2. **API Endpoint Mismatch: Missing repo_root in /api/summarize**
**Severity:** CRITICAL — Summarization will crash

#### Problem:
- **Frontend** (`useSummary.js` line 19): Sends `{ path: filePath }` only
- **Backend** (`models.py` lines 50-58): Expects:
  - `filepath` (relative path)
  - `repo_root` (absolute path to repo)
  - `language` (language string)
  - Optional: `content_hash`

#### Impact:
Frontend sends incomplete data. Backend will reject the request with validation errors.

#### Fix Required:
**Frontend must send complete SummarizeRequest:**
```javascript
const response = await axios.post('/api/summarize', {
  filepath: filePath,        // relative path
  repo_root: repoRoot,       // store this when analyzing graph
  language: language,        // from node data
  content_hash: contentHash  // optional
});
```

The frontend needs to:
1. Store `repo_root` from the graph analysis response
2. Pass `language` from the selected node's data
3. Pass `filepath` as relative path

---

### 3. **Missing API Base URL Configuration**
**Severity:** HIGH — API calls fail in production/custom ports

#### Problem:
- Frontend uses relative paths (`/api/graph`, `/api/summarize`)
- No configuration for backend base URL
- Works only if frontend and backend run on same origin

#### Fix Required:
**Create an API configuration file:**

```javascript
// frontend/src/utils/apiClient.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

Then update hooks to use this client.

---

### 4. **Node Data Field Mismatch**
**Severity:** MEDIUM — Frontend displays incorrect data

#### Problem:
- **Backend NodeModel** returns: `id, label, language, loc, total_lines, blank_lines, comment_lines, complexity, size_kb`
- **Frontend** expects (line 28-32 `useGraphData.js`): 
  - `node.path` (doesn't exist in backend response)
  - `node.type` (doesn't exist in backend response)

#### Current Frontend Code:
```javascript
data: {
  label: node.label,
  path: node.path,           // ❌ NOT in response
  language: node.language,
  loc: node.loc,
  complexity: node.complexity,
  fileType: node.type ?? 'file',  // ❌ NOT in response
},
```

#### Fix Required:
Backend should return `path` (or frontend should use `id`), and clarify how to determine `fileType`.

---

### 5. **CORS Configuration Incomplete**
**Severity:** MEDIUM — May fail with certain frontend deployments

#### Problem:
- Backend CORS allows `http://localhost:5173` and `http://localhost:3000`
- Frontend runs on Vite default (5173) — OK
- No support for HTTPS or production domains

#### Fix Required:
Update `main.py` CORS to be environment-aware:
```python
_allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
```

---

### 6. **Missing Error Handling Symmetry**
**Severity:** LOW-MEDIUM — Poor UX on failures

#### Problem:
- **Frontend** catches `err.response?.data?.detail`
- **Backend** returns errors with `detail` field ✓ (Good)
- But frontend doesn't handle missing `response` object (network failures)

#### Fix Required:
```javascript
catch (err) {
  const errorMsg = err.response?.data?.detail 
    || err.message 
    || 'An unknown error occurred';
  setError(errorMsg);
}
```

---

## ✅ WHAT'S WORKING WELL

1. **CORS Setup:** Backend correctly allows Vite dev server
2. **Response Models:** Pydantic models are well-documented
3. **Error HTTP Codes:** Backend uses appropriate status codes (400, 403, 404, 500)
4. **Health Check:** `/health` endpoint exists for liveness probes
5. **Caching:** Cache management endpoints exist but frontend doesn't use them

---

## 📋 INTEGRATION CHECKLIST

### Backend Changes Needed:
- [ ] Change `/api/graph` from GET to POST (or change frontend to GET)
- [ ] Ensure `/api/graph` response includes all expected fields
- [ ] Document expected node/edge structure clearly
- [ ] Add environment variable support for CORS origins
- [ ] Return `path` field in node response (or clarify use of `id`)

### Frontend Changes Needed:
- [ ] Update `useSummary.js` to send complete `SummarizeRequest` (filepath, repo_root, language)
- [ ] Store `repo_root` when analyzing graph
- [ ] Extract and pass `language` and `filepath` correctly from node data
- [ ] Create API client with configurable base URL
- [ ] Update both hooks to use centralized API client
- [ ] Improve error handling for network failures
- [ ] Add loading states for summarization

### Shared/Deployment:
- [ ] Document API contract clearly (add back `api-contract.md` if removed)
- [ ] Define environment variables for both frontend and backend
- [ ] Create deployment guide for non-localhost setups

---

## 🚀 IMMEDIATE ACTIONS

### Priority 1 (Do First):
1. Fix `/api/graph` endpoint method (POST or GET consistency)
2. Fix `useSummary.js` to send required fields

### Priority 2 (Do Next):
3. Create centralized API client
4. Add proper error handling

### Priority 3 (Polish):
5. Environment configuration
6. Documentation
