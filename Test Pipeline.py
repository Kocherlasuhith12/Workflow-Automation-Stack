#!/usr/bin/env python3
"""
Quick test — runs the full pipeline directly against FastAPI.
Use this to verify before wiring into n8n.

Usage:
    python test_pipeline.py
"""

import httpx
import json

FASTAPI_URL  = "http://localhost:8001/enrich-weather"
WEBHOOK_SITE = "https://webhook.site/YOUR-UNIQUE-ID"  # replace this

payload = {
    "city":        "Chennai",
    "country_code": "IN",
    "webhook_url": WEBHOOK_SITE,
}

print("🚀 Firing pipeline...")
print(f"   City:    {payload['city']}")
print(f"   Output:  {payload['webhook_url']}\n")

resp = httpx.post(FASTAPI_URL, json=payload, timeout=30)
resp.raise_for_status()

result = resp.json()
print("✅ Pipeline complete!\n")
print("── Enriched Payload ──────────────────────────────────")
print(json.dumps(result["enriched_payload"], indent=2))
print("\n── AI Summary ────────────────────────────────────────")
print(result["enriched_payload"]["ai_summary"])
print("\n── Webhook Response ──────────────────────────────────")
print(result["webhook_response"])