from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  
from ai_agent.match_agent import process_query

app = FastAPI()

# ✅ CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 Development mein * use kar sakte ho
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryInput(BaseModel):
    query: str

@app.post("/api/find-tutor")
async def find_tutor(input: QueryInput):
    result = await process_query(input.query)
    return result
