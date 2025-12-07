
# n8n-workflow-popularity-system


Automated Data Collection • YouTube • n8n Forum • Google Search Trends • MongoDB • FastAPI

This project is a complete automated workflow popularity tracking system designed to collect, score, and store popular n8n automation workflows from 3 major platforms:

- YouTube (tutorials, automation walkthroughs, integrations)

- n8n Community Forum (Showcase, Workflow templates, Built-with-n8n posts)

- Google Search Trends (public interest & keyword popularity)

All collected data is processed into a standardized popularity scoring format and saved into MongoDB, accessible via REST API.

The system also includes a GitHub Actions daily cron job that refreshes the dataset automatically every 24 hours.

## 🚀 Features

✅ 1. YouTube Popular Workflow Collection
- Fetches videos matching top n8n workflow keywords

- Popularity metrics extracted:

    - Views

    - Likes

    - Comments

    - Engagement ratios
✅ 2. n8n Forum Workflow Extraction

- Scrapes workflow-related categories:

    - Built with n8n

    - Workflow Templates

- Extracts:

    - Views

    - Replies

    - Likes (actual post likes using post actions)

    - Contributors

✅ 3. Google Search Trends Monitoring

Uses PyTrends to measure public interest across countries.

Metrics:

🔹 Relative search interest

🔹 30-day trend change

🔹 60-day trend change

🔹 Estimated search volume

Supports US & IN segmentation.

✅ 4. Unified REST API (FastAPI)

Fetch combined or platform-specific workflows:

#### Get Youtube workflow data

```http
  GET /youtube/data
```
#### Get Forum workflow data
```http
  GET /forum/data
```
#### Get Google Search/ Trends data
```http
  GET /google/data
```

#### Get All Workflows data
```http
  GET /workflows/all
```

✅ 5. MongoDB Storage

- All workflows stored in 2 collections:

- ```
    workflows (YouTube + Forum)
  ```
  
- ```
    trends (Google Search)
  ```
✅ 6. Automated Daily Cron Job (GitHub Actions)

- Runs every 24 hours:

- Fetches new YouTube workflows

- Fetches new Forum workflows

- Fetches updated Google Trends

- Saves all data to MongoDB
----

## 🔥 API Endpoints
📌 1. YouTube

▶ Fetch Preview (does NOT save)
```http
  GET /youtube/popular
```

💾 Save to MongoDB

```http
  POST /youtube/save
```
📥 Retrieve saved data

```http
  GET /youtube/data?country=US
```

📌 2. Forum
▶ Preview (no DB write)
```http
  GET /forum/fetch
```

💾 Save to MongoDB

```http
  POST /forum/save
```

📥 Retrieve saved data

```http
  GET /forum/data?country=IN
```

📌 3. Google Trends
▶ Preview

```http
  GET /google/fetch
```

💾 Save to MongoDB

```http
  POST /google/save
```

📥 Retrieve saved data

```http
  GET /google/data?country=US
```

📌 4. Combined API

```http
  GET /workflows/all?country=US
```
- Returns combined:

- YouTube workflows

- Forum workflows

- Google Trends workflows

## 🛠️ Tech Stack
| Component         | Tool / Library                    |
|------------------|------------------------------------|
| API Framework     | FastAPI                            |
| Database         | MongoDB                              |
|Cron Automation      | GitHub Actions |
| Data Sources               | YouTube API · Forum Scraper · Google Trends |
| Language | Python 3                          |

---------

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`MONGO_URI`

`DATABASE_NAME`

`YOUTUBE_API_KEY`

These are already deployed on render.

