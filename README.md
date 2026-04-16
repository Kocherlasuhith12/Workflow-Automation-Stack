# 🔄 Workflow Automation Stack

A fully local workflow automation system built with **n8n**, **Temporal**, **Restate**, and **FastAPI (Python)** — all running together via Docker.

---

## 🧱 Tech Stack

| Service | Role | Port |
|--------|------|------|
| **n8n** | Workflow automation & webhook trigger | `5678` |
| **Temporal** | Workflow orchestration & execution tracking | `8080` |
| **Restate** | Durable service execution | - |
| **FastAPI (Python)** | Backend API that connects everything | `8001` |

---

## 🏗️ Architecture

```
Webhook (curl / external)
        ↓
      n8n (localhost:5678)
        ↓
  FastAPI /start-workflow (localhost:8001)
        ↓
  Temporal Worker → Activities (Restate)
        ↓
  Result returned back to n8n
```

---

## 📁 Project Structure

```
workflow/
├── n8n/                  # n8n config and data
├── docker-compose.yml    # All services defined here
├── Dockerfile            # Python app Docker image
├── main.py               # FastAPI entry point
├── workflows.py          # Temporal workflow definitions
├── activities.py         # Temporal activity definitions
├── temporal_worker.py    # Temporal worker runner
├── service.py            # Restate service
├── register_restate.sh   # Script to register Restate handlers
└── requirements.txt      # Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) installed and running
- [Docker Compose](https://docs.docker.com/compose/) available
- Terminal / Command line

---

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd workflow
```

### 2. Start all services

```bash
docker compose up --build
```

This starts:
- **n8n** on `http://localhost:5678`
- **Temporal UI** on `http://localhost:8080`
- **FastAPI** on `http://localhost:8001`
- **Restate** (internal)

### 3. Verify everything is running

Open your browser and go to:
```
http://localhost:8001
```

You should see:
```json
{
  "status": "running",
  "services": ["temporal", "restate", "n8n"]
}
```

---

## ⚙️ Setting Up the n8n Workflow

### Step 1 — Open n8n
Go to `http://localhost:5678`

### Step 2 — Create a new workflow
- Click **"Add first step"**
- Search for **Webhook** and select it
- Set **HTTP Method** to `POST`
- Copy the **Test URL**

### Step 3 — Add HTTP Request node
- Click **"+"** after the Webhook node
- Search for **HTTP Request**
- Set:
  - **Method:** `POST`
  - **URL:** `http://host.docker.internal:8001/start-workflow`
  - **Body Content Type:** `JSON`
  - **Body Parameter:**
    - Name: `name`
    - Value: `{{ $json.body.name }}`

### Step 4 — Save and Publish
- Click **Save**
- Click **Publish**

---

## 🧪 Testing the Workflow

### Test Mode (during development)
1. Click the Webhook node in n8n
2. Click **"Listen for test event"**
3. Run:

```bash
curl -X POST "http://localhost:5678/webhook-test/<your-webhook-id>" \
  -H "Content-Type: application/json" \
  -d '{"name": "YourName"}'
```

### Live Mode (after publishing)

```bash
curl -X POST "http://localhost:5678/webhook/<your-webhook-id>" \
  -H "Content-Type: application/json" \
  -d '{"name": "YourName"}'
```

### Expected Response

```json
{
  "result": "Workflow completed for: Hello, {'name': 'YourName'}! Greetings from Restate 🌟"
}
```

---

## 📊 Monitoring

| Dashboard | URL | What to check |
|-----------|-----|---------------|
| **n8n Editor** | `http://localhost:5678` | Workflow runs, node status |
| **n8n Executions** | `http://localhost:5678` → Executions tab | Past runs, success/failure |
| **Temporal UI** | `http://localhost:8080` | Workflow history, status |
| **FastAPI Health** | `http://localhost:8001` | Service status |

---

## 🐳 Docker Notes

- n8n runs inside Docker, so use `host.docker.internal` instead of `localhost` when calling your FastAPI from n8n
- All services are defined in `docker-compose.yml`
- Python dependencies are in `requirements.txt`

---

## 🛠️ Useful Commands

```bash
# Start all services
docker compose up --build

# Stop all services
docker compose down

# View logs
docker compose logs -f

# Restart a specific service
docker compose restart <service-name>
```

---

## ✅ Proof of Working

The full workflow was tested end-to-end:

1. ✅ Webhook received by n8n
2. ✅ n8n called FastAPI at `/start-workflow`
3. ✅ FastAPI triggered a Temporal workflow
4. ✅ Temporal worker executed the activity via Restate
5. ✅ Result returned: *"Workflow completed"*
6. ✅ Temporal UI showed status: **Completed**

---

## 👤 Author

Built with Python + Docker as a local workflow automation proof of concept.
