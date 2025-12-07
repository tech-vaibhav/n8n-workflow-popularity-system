from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="n8n Workflow Popularity API",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def home():
    return {"message": "n8n Popularity System API is running!"}