<div align="center">

```
██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗███████╗██╗      ██████╗ ██╗    ██╗
██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██╔════╝██║     ██╔═══██╗██║    ██║
██║ █╗ ██║██║   ██║██████╔╝█████╔╝ █████╗  ██║     ██║   ██║██║ █╗ ██║ 
██║███╗██║██║   ██║██╔══██╗██╔═██╗ ██╔══╝  ██║     ██║   ██║██║███╗██║
╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗██║     ███████╗╚██████╔╝╚███╔███╔╝
 ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ 
```
 
### **Local Workflow Automation · Built for Resilience**
*n8n · Temporal · Restate · FastAPI — orchestrated via Docker*

![Status](https://img.shields.io/badge/status-production%20ready-22c55e?style=flat-square&labelColor=0f172a)
![Stack](https://img.shields.io/badge/stack-Python%20%7C%20Docker-3b82f6?style=flat-square&labelColor=0f172a)
![License](https://img.shields.io/badge/license-MIT-f97316?style=flat-square&labelColor=0f172a)
![Tests](https://img.shields.io/badge/end--to--end-passing-22c55e?style=flat-square&labelColor=0f172a)

</div> 

---

## What Is This?

A **fully local, resilient workflow automation system** that wires together four powerful tools — without touching any cloud. Every piece runs in Docker. You trigger a webhook, and the whole pipeline fires: n8n handles routing, Temporal guarantees execution, Restate makes services durable, and FastAPI ties it all together.

> Zero SaaS lock-in. Zero cold starts. Total observability.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WORKFLOW PIPELINE                        │
└─────────────────────────────────────────────────────────────────┘

  curl / external trigger
          │
          ▼
  ┌──────────────┐        Webhook received, workflow begins
  │     n8n      │  :5678
  │  (trigger +  │
  │   routing)   │
  └──────┬───────┘
         │  POST /start-workflow
         ▼
  ┌──────────────┐        Durable orchestration kicks in
  │   FastAPI    │  :8001
  │  (Python)    │
  └──────┬───────┘
         │  Starts Temporal workflow
         ▼
  ┌──────────────┐        Activity execution with retry guarantees
  │   Temporal   │  :8080
  │   Worker     │
  └──────┬───────┘
         │  Executes via Restate
         ▼
  ┌──────────────┐        Durable service call — survives crashes
  │   Restate    │
  │  (Service)   │
  └──────┬───────┘
         │
         ▼
     ✅ Result returned to n8n
```

---

## Tech Stack

| Service | Role | Port | Why It's Here |
|---------|------|------|---------------|
| **n8n** | Webhook trigger + workflow routing | `5678` | Visual automation, no-code friendly |
| **Temporal** | Durable orchestration + execution history | `8080` | Retry logic, fault tolerance, observability |
| **Restate** | Durable service execution | internal | Guarantees exactly-once activity execution |
| **FastAPI** | Python backend — the glue | `8001` | Clean REST surface, async-native |

---

## Project Structure

```
workflow/
├── 📄 docker-compose.yml       ← Boots all four services
├── 🐳 Dockerfile               ← Python app image
├── ⚡ main.py                  ← FastAPI entrypoint
├── 🔄 workflows.py             ← Temporal workflow definitions
├── ⚙️  activities.py           ← Temporal activity logic
├── 🏃 temporal_worker.py       ← Worker runner
├── 🛡️  service.py              ← Restate service definitions
├── 📜 register_restate.sh      ← Registers Restate handlers
├── 📦 requirements.txt         ← Python dependencies
└── 📁 n8n/                     ← n8n config + data volume
```

---

## Getting Started

### Prerequisites

- **Docker** — [Get it here](https://www.docker.com/)
- **Docker Compose** — bundled with Docker Desktop
- A terminal

### 1 — Clone

```bash
git clone <your-repo-url>
cd workflow
```

### 2 — Launch Everything

```bash
docker compose up --build
```

This single command boots all four services. Give it ~30 seconds on first run.

| Service | URL |
|---------|-----|
| n8n Editor | http://localhost:5678 |
| Temporal UI | http://localhost:8080 |
| FastAPI | http://localhost:8001 |

### 3 — Health Check

```bash
curl http://localhost:8001
```

Expected response:

```json
{
  "status": "running",
  "services": ["temporal", "restate", "n8n"]
}
```

---

## Setting Up the n8n Workflow

> Takes ~3 minutes. Do this once.

**Step 1** — Open `http://localhost:5678`

**Step 2** — Create a new workflow:
- Click **Add first step** → search for **Webhook** → select it
- Set HTTP Method to `POST`
- Copy the **Test URL**

**Step 3** — Add an HTTP Request node after the webhook:

| Field | Value |
|-------|-------|
| Method | `POST` |
| URL | `http://host.docker.internal:8001/start-workflow` |
| Body Content Type | `JSON` |
| Body Param Name | `name` |
| Body Param Value | `{{ $json.body.name }}` |

> **Why `host.docker.internal`?** n8n runs inside Docker — `localhost` refers to its own container, not your machine. `host.docker.internal` correctly points to the host.

**Step 4** — Hit **Save**, then **Publish**.

---

## Testing

### Development (Test Mode)

1. Click the Webhook node → **Listen for test event**
2. Fire a test request:

```bash
curl -X POST "http://localhost:5678/webhook-test/<your-webhook-id>" \
  -H "Content-Type: application/json" \
  -d '{"name": "KKS Suhith"}'
```

### Production (Live Mode)

```bash
curl -X POST "http://localhost:5678/webhook/<your-webhook-id>" \
  -H "Content-Type: application/json" \
  -d '{"name": "KKS Suhith"}'
```

### Expected Output

```json
{
  "result": "Workflow completed for: Hello, {'name': 'KKS Suhith'}! Greetings from Restate 🌟"
}
```

---

## Monitoring Dashboards

| Dashboard | URL | What to Watch |
|-----------|-----|---------------|
| **n8n Workflows** | http://localhost:5678 | Node status, run history |
| **n8n Executions** | http://localhost:5678/executions | Success/failure log |
| **Temporal UI** | http://localhost:8080 | Workflow history, retry state |
| **FastAPI Health** | http://localhost:8001 | Service liveness |

---

## Common Commands

```bash
# Start everything
docker compose up --build

# Start in background
docker compose up -d --build

# View live logs
docker compose logs -f

# Restart a specific service
docker compose restart fastapi

# Stop and remove containers
docker compose down

# Nuke volumes (fresh start)
docker compose down -v
```

---

## End-to-End Test Results

```
✅  Webhook received by n8n
✅  n8n → FastAPI /start-workflow called
✅  FastAPI → Temporal workflow triggered
✅  Temporal Worker executed activity via Restate
✅  Result returned: "Workflow completed"
✅  Temporal UI status: Completed
```

All 6 stages verified. Pipeline is green.

---

## Why This Stack?

| Concern | How It's Solved |
|---------|----------------|
| **Workflow crashes mid-run?** | Temporal automatically retries from the last checkpoint |
| **Service called twice by mistake?** | Restate guarantees exactly-once execution |
| **Need to trigger without writing code?** | n8n webhook handles it visually |
| **Want a clean API surface?** | FastAPI with async Python |
| **Everything cloud-dependent?** | Nope. 100% local via Docker |

---

<div align="center">

Built with Python + Docker · Proof of concept for production-grade local automation

</div>
