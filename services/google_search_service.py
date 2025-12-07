from services.trends_service import GOOGLE_SEARCH_KEYWORDS, get_trend_data
from database.mongodb import get_db

def fetch_google_search_preview(max_keywords=200):
    """Return trend data for keywords without saving to DB."""
    keywords = GOOGLE_SEARCH_KEYWORDS[:max_keywords]

    results = []

    for kw in keywords:
        trends = get_trend_data(kw)

        results.append({
            "keyword": kw,
            "US": trends["US"],
            "IN": trends["IN"]
        })

    return results


def save_google_search_data(max_keywords=200):
    db = get_db()
    keywords = GOOGLE_SEARCH_KEYWORDS[:max_keywords]

    inserted = 0

    for kw in keywords:
        trends = get_trend_data(kw)

        # US Entry
        us_entry = {
            "keyword": kw,
            "platform": "Google Search",
            "country": "US",
            "popularity_metrics": trends["US"]
        }
        db.workflows.update_one(
            {"keyword": kw, "platform": "Google Search", "country": "US"},
            {"$set": us_entry},
            upsert=True
        )
        inserted += 1

        # India Entry
        in_entry = {
            "keyword": kw,
            "platform": "Google Search",
            "country": "IN",
            "popularity_metrics": trends["IN"]
        }
        db.workflows.update_one(
            {"keyword": kw, "platform": "Google Search", "country": "IN"},
            {"$set": in_entry},
            upsert=True
        )
        inserted += 1

    return {"status": "success", "keywords_processed": len(keywords), "inserted": inserted}
