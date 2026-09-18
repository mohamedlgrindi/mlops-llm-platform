#  Production-Grade Autonomous LLM Serving & MLOps Platform

An enterprise-grade, microservice-based MLOps platform built to deploy, serve, stream, and monitor quantized open-source Large Language Models (LLMs) with low latency and high throughput.

The system implements a **$0 GPU Hybrid Architecture**: a local Kubernetes API gateway handles validation, metrics, and routing, while offloading high-concurrency model execution to an NVIDIA T4 GPU running `vLLM` via a secure HTTPS tunnel.

##  Key Technical Features

- **Asynchronous Token Streaming (SSE):** Utilizes FastAPI's `StreamingResponse` and Server-Sent Events (SSE) to stream generated text tokens in real time, drastically reducing Time-To-First-Token (TTFT).
- **Decoupled Strategy Pattern:** Implements a decoupled engine abstraction (`MockLLMEngine` vs. `RemotevLLMEngine`) managed via FastAPI's `@asynccontextmanager` lifespan event handler, preventing redundant model reloading and enabling zero-downtime engine swapping.
- **$0 GPU Offloading Architecture:** Connects local Kubernetes/WSL gateways to a Google Colab NVIDIA T4 GPU running `vLLM` (`Qwen/Qwen2.5-0.5B-Instruct`) over an `ngrok` encrypted HTTPS tunnel.
- **Schema Validation & Guardrails:** Enforces strict parameter validation (`max_tokens`, `temperature`) using `Pydantic` schemas to prevent out-of-bounds execution and VRAM overflow.
- **Multi-Stage Containerization:** Utilizes multi-stage `Docker` builds optimizing image sizes, runtime isolation, and layer caching.
- **Kubernetes Orchestration & Helm Packaging:** Deploys resilient microservices with automated self-healing (`livenessProbe`, `readinessProbe`), resource constraints, NodePort services, and parameterized `Helm v3` charts.
- **Production Observability Stack:** Instrumented with `prometheus-fastapi-instrumentator` to export HTTP throughput, status codes, and p95/p99 latency metrics into Prometheus TSDB and Grafana dashboards.
- **Automated CI/CD Pipeline:** Uses `GitHub Actions` to run automated `PyTest` suites, execute schema validations, and test container builds on every push or pull request.

##  System Architecture & Data Flow

The platform follows a decoupled, microservice-oriented topology:

1. **Client / Request Layer:** The client initiates an asynchronous `POST /generate` request containing JSON prompt payloads and sampling parameters.
2. **API Gateway & Schema Validation (FastAPI + Pydantic):** The local gateway receives the request, validates bounds via `PromptRequest`, and records HTTP counters.
3. **Lifespan Engine Delegation (`app.state.engine`):** The gateway fetches the active warm engine instance from memory. Depending on configuration:
   - **Local Mode:** `MockLLMEngine` streams token blocks for offline CPU testing.
   - **Remote GPU Mode:** `RemotevLLMEngine` sends an asynchronous `httpx` stream across an ngrok tunnel to the GPU host.
4. **GPU Acceleration Layer (`vLLM` on Google Colab):** An NVIDIA T4 GPU executes inference on `Qwen2.5-0.5B-Instruct` using PagedAttention memory management, streaming Server-Sent Events back through the tunnel.
5. **Observability Pipeline (Prometheus + Grafana):** Prometheus scrapes `/metrics` every 15 seconds from the application pods, feeding real-time time-series data into Grafana dashboards.

6. ## 🛠️ Technology Stack

| Domain | Technology / Tool | Functionality |
|---|---|---|
| API & Gateway | Python 3.10, FastAPI, Pydantic, Uvicorn | REST Gateway, schema validation, SSE streaming |
| ML Engine & Serving | vLLM, Hugging Face, PyTorch, CUDA | PagedAttention, GPU memory management, token generation |
| Testing & Quality | PyTest, FastAPI TestClient, httpx | Automated unit testing, lifespan fixture integration |
| Containerization | Docker (Multi-stage slim build) | Lightweight, reproducible runtime environment |
| Orchestration | Kubernetes (Minikube / K3s), Helm v3 | Auto-healing pods, NodePort routing, parameterized charts |
| Observability | Prometheus, Grafana, kube-prometheus-stack | Time-series metrics collection, p95 latency visualization |
| Automation / CI | GitHub Actions | Automated build, test, and container compilation pipeline |

## 📁 Repository Directory Structure

```
mlops-llm-platform/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD pipeline
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI gateway & lifespan manager
│   ├── engine.py                # Mock & Remote vLLM engine implementations
│   ├── schemas.py                # Pydantic data validation models
│   └── requirements.txt           # Production dependencies
├── docker/
│   └── Dockerfile                 # Multi-stage production container build
├── helm/
│   └── llm-platform/               # Helm v3 Chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           └── service.yaml
├── k8s/
│   ├── deployment.yaml               # Raw Kubernetes Deployment manifest
│   └── service.yaml                   # Raw Kubernetes Service manifest
├── monitoring/                         # Prometheus and Grafana configurations
├── test_main.py                         # PyTest unit test suite with lifespan fixtures
├── .gitignore
└── README.md                             # System documentation
```

## 🚀 Step-by-Step Quickstart Guide

### 1. Local Development Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_GITHUB_USERNAME/mlops-llm-platform.git
cd mlops-llm-platform

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt

# Run automated tests
pytest -v

# Launch local API gateway in mock mode
uvicorn app.main:app --reload --port 8000
```

Verify status at `http://127.0.0.1:8000/health` or open interactive documentation at `http://127.0.0.1:8000/docs`.

### 2. Docker Containerization

```bash
# Build the multi-stage Docker image
docker build -t mlops-llm-platform:v1 -f docker/Dockerfile .

# Run container locally
docker run -p 8000:8000 mlops-llm-platform:v1
```

### 3. Kubernetes & Helm Deployment

```bash
# Start local Minikube cluster
minikube start --driver=docker

# Load local image into Minikube
minikube image load mlops-llm-platform:v1

# Option A: Deploy raw manifests
kubectl apply -f k8s/

# Option B: Deploy via Helm v3
helm install llm-release helm/llm-platform/

# Check cluster status
kubectl get pods
kubectl get svc

# Port-forward service to local host
kubectl port-forward svc/llm-api-service 8000:8000
```

### 4. Observability Stack Setup (Prometheus & Grafana)

```bash
# Add official Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus & Grafana stack in 'monitoring' namespace
helm install prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Retrieve Grafana admin password
kubectl get secret -n monitoring prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode; echo

# Forward Grafana web dashboard
kubectl port-forward -n monitoring svc/prometheus-stack-grafana 3000:80
```

Open `http://localhost:3000` (Username: `admin`).

### 5. Remote GPU Offloading Setup (Google Colab + vLLM)

1. Open a Google Colab notebook and set runtime to **T4 GPU**.
2. Run installation:
```bash
   !pip uninstall -y torchaudio torchvision
   !pip install vllm torch fastapi uvicorn pyngrok nest_asyncio
```
3. Execute the vLLM server cell (patching `ipykernel` stdout and initializing `AsyncEngineArgs` with `gpu_memory_utilization=0.35` and `enforce_eager=True`).
4. Copy the live `ngrok` URL output (e.g., `https://xxxx.ngrok-free.dev/remote-generate`).
5. Launch your local gateway passing the environment variable:
```bash
   COLAB_URL="https://xxxx.ngrok-free.dev/remote-generate" uvicorn app.main:app --reload --port 8000
```


## 📡 API Reference & Usage Examples

### Health Check Endpoint

- **HTTP Method:** `GET /health`
- **Response `200 OK`:**
```json
  {
    "status": "healthy",
    "service": "llm-serving-api"
  }
```

### Streaming LLM Token Endpoint

- **HTTP Method:** `POST /generate`
- **Header:** `Content-Type: application/json`
- **Payload:**
```json
  {
    "prompt": "Explain MLOps in two sentences:",
    "max_tokens": 60,
    "temperature": 0.7
  }
```
- **Streaming Response** (`text/event-stream`):
```
  data: MLOps
  data:  combines
  data:  software
  data:  engineering
  data:  and
  data:  machine
  data:  learning
  data:  to
  data:  automate
  data:  model
  data:  deployments.
  data: [DONE]
```
## 🧪 Automated Testing & CI/CD Pipeline

The platform enforces quality checks using `PyTest` fixtures that execute against FastAPI's `lifespan` manager:

```bash
# Execute local unit tests
pytest -v
```

Every push to the `main` branch triggers `.github/workflows/ci.yml`, which automatically:

1. Provisions a clean `ubuntu-latest` runner.
2. Configures Python `3.10` runtime.
3. Installs dependencies from `app/requirements.txt`.
4. Executes unit tests via `pytest`.
5. Compiles and verifies the multi-stage `Dockerfile`.
