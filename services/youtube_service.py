import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
from database.mongodb import get_db

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

SEARCH_QUERIES = [
    "Amazing n8n workflows",
    "n8n tutorial",
    "n8n slack automation",
    "n8n google sheets automation"
]

def search_videos(query, max_pages=1):
    videos = []
    next_page_token = None

    for _ in range(max_pages):
        response = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            order="viewCount",
            maxResults=25,
            pageToken=next_page_token
        ).execute()

        videos.extend(response.get("items", []))

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos


def fetch_youtube_workflows(max_results=50):
    db = get_db()
    
    #Get cached video_ids form db
    existing_ids = set(db.workflows.distinct("video_id"))
    
    videos = []
    seen_ids = set()
    
    for query in SEARCH_QUERIES:
        search_results = search_videos(query)

        for item in search_results:
            video_id = item["id"]["videoId"]
            
            # Skip if already fetched before
            if video_id in existing_ids:
                continue

            if video_id in seen_ids:
                continue
            seen_ids.add(video_id)

            video_details = youtube.videos().list(
                part="statistics,snippet",
                id=video_id
            ).execute()

            if not video_details["items"]:
                continue
            
            details = video_details["items"][0]
            stats = details.get("statistics", {})

            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))

            like_ratio = round(likes / views, 2) if views > 0 else 0
            comment_ratio = round(comments / views, 2) if views > 0 else 0

            popularity_score = (views * 0.6) + (likes * 2) + (comments * 3)

            videos.append({
                "workflow": query,
                "video_title": details["snippet"]["title"],
                "video_id": video_id,
                "platform": "YouTube",
                "popularity_metrics": {
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "like_to_view_ratio": like_ratio,
                    "comment_to_view_ratio": comment_ratio,
                    "popularity_score": popularity_score
                }
            })

    # Sort by popularity
    videos = sorted(videos, key=lambda x: x["popularity_metrics"]["popularity_score"], reverse=True)

    return videos[:max_results]

def save_youtube_workflows_to_db(max_results=50):
    db = get_db()
    videos = fetch_youtube_workflows(max_results=max_results)
    
    inserted_records = 0

    for video in videos:
        keyword = video["workflow"]
        
        us_entry = {
            **video,
            "country": "US"
        }
        
        db.workflows.update_one(
            {"video_id": video["video_id"], "platform": "YouTube", "country": "US"},
            {"$set": us_entry},
            upsert=True
        )
        inserted_records += 1
        
        in_entry = {
            **video,
            "country": "IN"
        }

        # Insert or update (UPSERT)
        db.workflows.update_one(
            {"video_id": video["video_id"], "platform": "YouTube", "country": "IN"},
            {"$set": in_entry},
            upsert=True
        )
        inserted_records += 1
    
    return {"status": "success", "inserted": inserted_records}