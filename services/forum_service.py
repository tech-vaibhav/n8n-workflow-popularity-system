import requests
from database.mongodb import get_db

BASE_URL = "https://community.n8n.io"

# 5 workflow-related categories
CATEGORY_ENDPOINTS = {
    "built_with_n8n": "c/15.json", 
    "workflow_templates": "c/workflows/28.json"
}

# How many pages to fetch per category
MAX_PAGES = 10


VALID_KEYWORDS = [
    "n8n", "workflow automation", "build", 
    "workflow", "automation", "integrate", "bot",
    "sync", "email", "reminder", "trigger", "webhook", 
    "slack", "whatsapp", "telegram", "google sheets",
    "notion", "crm", "zapier", "calendar", "api",
    "scraper", "ai agent", "pipeline", "linkedin", "openai",
    "gemini", "github", "langchain", "rag"
]

def is_valid_workflow(title: str):
    """Check if topic title represents a workflow."""
    title = title.lower()
    return any(word in title for word in VALID_KEYWORDS)

def fetch_category_topics(endpoint, pages=MAX_PAGES):
    """Fetch topics from category with pagination."""
    topics = []

    for page in range(pages):
        url = f"{BASE_URL}/{endpoint}?page={page}"
        try:
            resp = requests.get(url, timeout=10)
        except:
            continue

        if resp.status_code != 200:
            continue

        data = resp.json()
        items = data.get("topic_list", {}).get("topics", [])
        topics.extend(items)

    return topics

def fetch_topic_details(topic_id):
    """Fetch full topic details: likes, posts etc."""
    url = f"{BASE_URL}/t/{topic_id}.json"
    try:
        resp = requests.get(url, timeout=8)
    except:
        return None

    if resp.status_code != 200:
        return None

    return resp.json()

def extract_likes(details):
    posts = details.get("post_stream", {}).get("posts", [])
    total = 0
    for post in posts:
        for action in post.get("actions_summary", []):
            if action.get("id") == 2:  # LIKE
                total += action.get("count", 0)
    return total

def extract_workflow(topic, details):
    """Create workflow entry with popularity metrics."""

    topic_id = topic["id"]
    title = topic["title"]
    views = topic.get("views", 0) 
    replies = topic.get("reply_count", 0)

    # Unique contributors from posters list
    posters = topic.get("posters", [])
    contributors = len(posters)

    # # likes from each post in thread
    # likes = details.get("like_count") or topic.get("like_count", 0)

    likes = extract_likes(details)

    # popularity score
    popularity_score = (
        (views * 0.5) + 
        (replies * 5) + 
        (likes * 3) + 
        (contributors * 2)
    )

    return {
        "workflow": title,
        "topic_id": topic_id,
        "platform": "Forum",
        "popularity_metrics": {
            "views": views,
            "replies": replies,
            "likes": likes,
            "unique_contributors": contributors,
            "popularity_score": popularity_score
        }
    }


def fetch_forum_workflows(max_results=3000):
    db = get_db()
    existing_ids = set(db.workflows.distinct("topic_id"))

    workflows = []

    # Fetch from all categories
    for category, endpoint in CATEGORY_ENDPOINTS.items():
        topics = fetch_category_topics(endpoint)

        for topic in topics:
            title = topic["title"]
            
            # Filter irrelevant topics
            if not is_valid_workflow(title):
                continue
            
            topic_id = topic["id"]

            # skip cached topics
            if topic_id in existing_ids:
                continue

            details = fetch_topic_details(topic_id)
            if not details:
                continue

            workflow_data = extract_workflow(topic, details)
            workflows.append(workflow_data)

            if len(workflows) >= max_results:
                return workflows

    return workflows

def save_forum_workflows_to_db(max_results=1000):
    db = get_db()
    workflows = fetch_forum_workflows(max_results=max_results)

    inserted = 0

    for wf in workflows:

        # US entry
        us_entry = {
            **wf,
            "country": "US"
        }
        db.workflows.update_one(
            {"topic_id": wf["topic_id"], "platform": "Forum", "country": "US"},
            {"$set": us_entry},
            upsert=True
        )
        inserted += 1

        # IN entry
        in_entry = {
            **wf,
            "country": "IN"
        }
        db.workflows.update_one(
            {"topic_id": wf["topic_id"], "platform": "Forum", "country": "IN"},
            {"$set": in_entry},
            upsert=True
        )
        inserted += 1

    return {"status": "success", "inserted": inserted}
