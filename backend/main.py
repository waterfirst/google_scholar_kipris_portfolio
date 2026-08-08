"""backend/main.py — FastAPI Portfolio API Server"""
import sys
from pathlib import Path

# Ensure backend is in path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from services.portfolio import PortfolioService

app = FastAPI(
    title="Research Portfolio API",
    description="Google Scholar + KIPRIS integrated research portfolio generator",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Models ----
class SearchRequest(BaseModel):
    name: str
    scholar_id: str = ""      # optional Google Scholar user ID
    include_papers: bool = True
    include_patents: bool = True

class SearchResponse(BaseModel):
    success: bool
    name: str
    error: str = ""
    profile: dict = {}
    kr_patents: list = []
    us_patents: list = []
    papers: list = []
    charts: dict = {}
    summary: dict = {}

# ---- API Routes ----
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Research Portfolio API", "version": "2.0.0"}

@app.post("/api/search", response_model=SearchResponse)
async def search_portfolio(req: SearchRequest):
    """Search and generate portfolio for a researcher by name."""
    name = req.name.strip()
    if not name:
        raise HTTPException(400, "Name is required")

    result = await PortfolioService.generate(name)
    return SearchResponse(
        success=result.success,
        name=result.name,
        error=result.error,
        profile=result.profile,
        kr_patents=result.kr_patents if req.include_patents else [],
        us_patents=result.us_patents if req.include_patents else [],
        papers=result.papers if req.include_papers else [],
        charts=result.charts,
        summary=result.summary,
    )

@app.get("/api/portfolio/{name}")
async def get_portfolio(name: str):
    """Quick GET endpoint for portfolio generation."""
    result = await PortfolioService.generate(name)
    if not result.success:
        raise HTTPException(404, result.error)
    return {
        "success": True,
        "name": result.name,
        "profile": result.profile,
        "kr_patents": result.kr_patents,
        "us_patents": result.us_patents,
        "papers": result.papers,
        "charts": result.charts,
        "summary": result.summary,
    }

# ---- Serve Frontend ----
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

    @app.get("/")
    async def serve_frontend():
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "Frontend not built. Visit /docs for API."}

# ---- Startup ----
if __name__ == "__main__":
    import uvicorn, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    print("\n" + "=" * 60)
    print("  Research Portfolio API Server")
    print("  http://localhost:8000        -- Frontend")
    print("  http://localhost:8000/docs   -- API Docs (Swagger)")
    print("  http://localhost:8000/api/health -- Health Check")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
