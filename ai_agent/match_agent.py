import os
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel, Runner
from sanity_client import fetch_tutors
try:
    from openai import RateLimitError, APIError
except Exception:  # pragma: no cover
    class RateLimitError(Exception): ...
    class APIError(Exception): ...
    
load_dotenv()

# Gemini Config
gemini_api_key = os.getenv("GEMINI_API_KEY")
base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

if not gemini_api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file!")

# Gemini as OpenAI wrapper
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url=base_url
)

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",  # Use pro for better understanding
    openai_client=provider
)

config = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True
)

# Output schema
class TutorFilterOutput(BaseModel):
    subject: str
    location: str
    gender: str
    mode: str

# 🔥 Advanced Instructions for better language understanding
advanced_prompt = """
You are an intelligent assistant helping users find tutors.

Users may write in casual English or Roman Urdu, and not always follow grammar rules.

Your job is to extract these 1 values:
- subject (like: math, physics)
- location (like: Nazimabad)
- gender (male/female)
- mode (Online/Home/Institute)

Be smart and flexible. Even if the user doesn't mention all fields clearly, try your best to infer the values based on context.

ALWAYS return lowercase values for all fields.
"""

# Gemini Agent
tutor_filter_agent = Agent(
    name="Smart Filter Extractor",
    instructions=advanced_prompt,
    output_type=TutorFilterOutput,
    model=model
)

# Main AI handler
async def process_query(query: str):
    result = await Runner.run(
        tutor_filter_agent,
        input=[{"role": "user", "content": query}],
        run_config=config
    )

    final_output = result.final_output_as(TutorFilterOutput)
    filters = final_output.model_dump()

    # 🎯 Lowercase all filter values (safe layer)
    filters = {k: v.lower() for k, v in filters.items()}

    # Sanity query
    tutors = fetch_tutors(filters)

    return {
        "filters": filters,
        "matchingTutors": tutors,
        "status": "ok"
    }
