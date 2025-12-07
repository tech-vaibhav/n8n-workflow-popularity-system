import time
import random
from datetime import datetime
from pytrends.request import TrendReq
from database.mongodb import get_db

# Initialize PyTrends
pytrends = TrendReq(hl="en-US", tz=330)

# FIXED KEYWORDS FOR n8n POPULAR WORKFLOW DISCOVERY
KEYWORDS = [
    "n8n",
    "n8n automation",
    "n8n tutorial",
    "n8n workflows",
    "n8n examples",
    "n8n integrations",
    "no code automation",
    "zapier alternative",
    "workflow automation",
    "google sheets automation"
]


BATCH_SIZE = 5
COUNTRIES = ["US", "IN"]

SAFE_SLEEP = 10  # 10 sec wait between batches

# -------------------------------
# Utility Functions
# -------------------------------

def calculate_trend_change(series, days=30):
    """Compute trend direction based on last N days."""
    if len(series) < days:
        return 0

    old_avg = series[:-days].mean()
    new_avg = series[-days:].mean()

    if old_avg == 0:
        return 0

    return round(((new_avg - old_avg) / old_avg) * 100, 2)


def estimate_search_volume(interest_value):
    """Approximate monthly search volume."""
    return int(interest_value * 60)  # safe heuristic


# -------------------------------
# Safe Trend Batch Fetch with Backoff
# -------------------------------

def fetch_trends_batch_safe(keywords, geo="US"):
    """
    Safely fetch trend data:
    - exponential backoff for 429
    - sleeps 10 sec between requests
    """
    backoff = 5

    while True:
        try:
            pytrends.build_payload(keywords, geo=geo, timeframe="today 3-m")
            data = pytrends.interest_over_time()

            return data

        except Exception as e:
            print(f"[WARN] Trends error for {keywords} in {geo}: {e}")

            if "429" in str(e) or "TooManyRequests" in str(e):
                print(f"[RATE LIMIT] Waiting {backoff} seconds...")
                time.sleep(backoff)
                backoff *= 2  # exponential increase
                if backoff > 60:
                    print(" [ERROR] Backoff too large, skipping batch.")
                    return None
            else:
                return None


# -------------------------------
# Main Fetch Logic
# -------------------------------

def fetch_search_trends(max_results=500):
    db = get_db()
    existing = db.trends.distinct("keyword")  # cached keywords

    results = []

    # Only fetch NEW keywords
    keywords_to_fetch = [kw for kw in KEYWORDS if kw not in existing]

    if not keywords_to_fetch:
        return []

    # Process in batches
    for i in range(0, len(keywords_to_fetch), BATCH_SIZE):
        batch = keywords_to_fetch[i:i + BATCH_SIZE]

        for country in COUNTRIES:

            # Fetch safely with backoff
            df = fetch_trends_batch_safe(batch, geo=country)

            # Wait after each batch
            print(f"[SLEEP] Waiting {SAFE_SLEEP} seconds before next batch...")
            time.sleep(SAFE_SLEEP)

            if df is None:
                continue

            for kw in batch:
                if kw not in df.columns:
                    continue

                series = df[kw]

                latest_interest = int(series.iloc[-1])
                change_30 = calculate_trend_change(series, 30)
                change_60 = calculate_trend_change(series, 60)

                results.append({
                    "workflow": kw,                     # REQUIRED FORMAT
                    "platform": "Google",               # Match YouTube / Forum style
                    "country": country,
                    "popularity_metrics": {
                        "relative_interest": latest_interest,
                        "trend_change_30d": change_30,
                        "trend_change_60d": change_60,
                        "estimated_search_volume": estimate_search_volume(latest_interest)
                    },
                    "timestamp": datetime.utcnow()
                })

                if len(results) >= max_results:
                    return results[:max_results]

    return results[:max_results]


# -------------------------------
# Save to DB
# -------------------------------

def save_search_trends_to_db(max_results=500):
    db = get_db()

    items = fetch_search_trends(max_results=max_results)
    inserted = 0

    for item in items:
        db.trends.update_one(
            {
                "workflow": item["workflow"],
                "country": item["country"],
                "platform": "Google"
            },
            {"$set": item},
            upsert=True
        )
        inserted += 1

    return {"status": "success", "inserted": inserted}
