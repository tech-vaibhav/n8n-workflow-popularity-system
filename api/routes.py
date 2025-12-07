from fastapi import APIRouter,Query 
from services.youtube_service import fetch_youtube_workflows, save_youtube_workflows_to_db
from services.forum_service import fetch_forum_workflows, save_forum_workflows_to_db
from services.trends_service import fetch_search_trends, save_search_trends_to_db
from database.mongodb import get_db

router = APIRouter()

@router.get("/")
def api_status():
    return {"status": "API routes working"}

@router.get("/youtube/popular")
def youtube_popular_workflows():
    data = fetch_youtube_workflows()
    return {"count": len(data), "data": data}

@router.post("/youtube/save")
def save_all_youtube():
    result = save_youtube_workflows_to_db()
    return result

@router.get("/youtube/data")
def get_youtube_data(country: str | None = None):
    db = get_db()
    query = {"platform": "YouTube"}
    if country:
        query["country"] = country

    data = list(db.workflows.find(query, {"_id": 0}))
    return {"count": len(data), "data": data}


@router.get("/forum/fetch")
def forum_fetch_preview(max_results: int = Query(50, ge=1, le=5000)):
    """
    Fetch forum workflows from n8n categories but do NOT save to DB.
    Use this to preview data and verify extraction.
    """
    items = fetch_forum_workflows(max_results=max_results)
    return {"count": len(items), "data_sample": items}

@router.post("/forum/save")
def forum_save(max_results: int = Query(1000, ge=1, le=10000)):
    """
    Fetch forum workflows and save to MongoDB (US + IN entries).
    Returns number of inserted records (2 per workflow).
    """
    result = save_forum_workflows_to_db(max_results=max_results)
    return result

@router.get("/forum/data")
def get_forum_data(country: str | None = None):
    db = get_db()
    query = {"platform": "Forum"}
    if country:
        query["country"] = country

    data = list(db.workflows.find(query, {"_id": 0}))
    return {"count": len(data), "data": data}


@router.get("/google/fetch")
def google_fetch_preview(max_results: int = 50):
    data = fetch_search_trends(max_results=max_results)
    return {"count": len(data), "data": data}

@router.post("/google/save")
def google_save(max_results: int = 200):
    result = save_search_trends_to_db(max_results=max_results)
    return result

@router.get("/google/data")
def get_google_data(country: str | None = None):
    db = get_db()
    query = {"platform": "Google"}
    if country:
        query["country"] = country

    data = list(db.trends.find(query, {"_id": 0}))
    return {"count": len(data), "data": data}

@router.get("/workflows/all")
def get_all_workflows(country: str | None = None):
    db = get_db()

    workflows = list(db.workflows.find({}, {"_id": 0}))
    trends = list(db.trends.find({}, {"_id": 0}))

    if country:
        workflows = [w for w in workflows if w["country"] == country]
        trends = [t for t in trends if t["country"] == country]

    combined = workflows + trends

    return {
        "count": len(combined),
        "data": combined
    }
