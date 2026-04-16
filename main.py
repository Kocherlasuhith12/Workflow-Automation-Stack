from fastapi import FastAPI
from temporalio.client import Client
import requests

app = FastAPI()


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)