from fastapi import FastAPI
from temporalio.client import Client
import requests
import httpx
import os
from pydantic import BaseModel

app = FastAPI()
 

# ── Models ────────────────────────────────────────────────────────────────────

class WeatherEnrichRequest(BaseModel):
    city: str
    country_code: str = "IN"
    webhook_url: str


# ── Config ────────────────────────────────────────────────────────────────────

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY",   "YOUR_ANTHROPIC_KEY_HERE")
OPENWEATHER_URL     = "https://api.openweathermap.org/data/2.5/weather"


# ── Existing Routes ───────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {"status": "running", "services": ["temporal", "restate", "n8n"]}


@app.post("/start-workflow")
async def start_workflow(name: str = "Suhith"):
    """
    Triggers a Temporal workflow.
    The workflow internally calls Restate via an activity.
    """
    client = await Client.connect("temporal:7233")

    from workflows import MyWorkflow

    result = await client.execute_workflow(
        MyWorkflow.run,
        name,
        id=f"workflow-{name}",
        task_queue="my-task-queue",
    )

    return {"result": result}


@app.post("/call-restate")
def call_restate(name: str = "test"):
    """
    Direct call to Restate service (bypasses Temporal).
    Useful for testing Restate standalone.
    """
    res = requests.post(
        "http://restate:8080/greeter/greet",
        json={"name": name},
        headers={"Content-Type": "application/json"},
    )
    return {"restate_response": res.text, "status_code": res.status_code}


# ── New: Weather AI Pipeline ──────────────────────────────────────────────────

async def fetch_weather(city: str, country_code: str) -> dict:
    params = {
        "q":     f"{city},{country_code}",
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPENWEATHER_URL, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()


async def ai_summarize(weather: dict) -> str:
    prompt = f"""
You are a concise weather assistant. Given the following weather data,
write a single punchy 2-sentence summary a developer would appreciate.
Be specific — mention numbers. Do not use markdown.

City: {weather['name']}
Temperature: {weather['main']['temp']}°C (feels like {weather['main']['feels_like']}°C)
Condition: {weather['weather'][0]['description']}
Humidity: {weather['main']['humidity']}%
Wind: {weather['wind']['speed'] * 3.6:.1f} kph
"""
    headers = {
        "x-api-key":         ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json",
    }
    body = {
        "model":      "claude-haiku-4-5-20251001",
        "max_tokens": 200,
        "messages":   [{"role": "user", "content": prompt}],
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=body,
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"].strip()


async def post_to_webhook(webhook_url: str, payload: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        return {"status": resp.status_code, "body": resp.text}


@app.post("/enrich-weather")
async def enrich_weather(req: WeatherEnrichRequest):
    """
    Full chain:
      1. Fetch raw weather from OpenWeatherMap
      2. Summarize with Claude AI
      3. POST enriched payload to req.webhook_url
    """
    # 1. Fetch
    raw = await fetch_weather(req.city, req.country_code)

    # 2. AI summarize
    summary = await ai_summarize(raw)

    # 3. Build enriched payload
    enriched = {
        "city":             raw["name"],
        "country":          raw["sys"]["country"],
        "temperature_c":    raw["main"]["temp"],
        "feels_like_c":     raw["main"]["feels_like"],
        "humidity_percent": raw["main"]["humidity"],
        "condition":        raw["weather"][0]["description"],
        "wind_kph":         round(raw["wind"]["speed"] * 3.6, 1),
        "ai_summary":       summary,
        "source":           "OpenWeatherMap + Claude AI",
    }

    # 4. Forward to webhook
    webhook_result = await post_to_webhook(req.webhook_url, enriched)

    return {
        "status":           "pipeline_complete",
        "enriched_payload": enriched,
        "webhook_response": webhook_result,
    }


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
