import httpx
from temporalio import activity

@activity.defn
async def call_restate_activity(name: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://restate:8080/greeter/greet",
            json={"name": name},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return response.text