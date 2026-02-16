# Voice Summarize Platform

Production-oriented, dockerized full-stack application that:

1. Accepts long voice/audio uploads (for example, 1 hour)
2. Summarizes content to a user-selected duration and genre
3. Generates output audio in the same speaker voice (reference-based cloning)
4. Runs with local Llama 3 orchestration via LangGraph

## Repository Structure

- `backend/`: FastAPI backend, domain/application layers, tests
- `frontend/`: AngularJS MVC UI
- `infra/docker/`: all Docker assets (compose, Dockerfiles, nginx config)
- `data/`: all runtime/generated data
  - `data/uploads/`: uploaded source audio
  - `data/outputs/`: generated summaries/transcripts
  - `data/ollama/`: local Ollama model cache (when using compose)

## Stack

- Backend: FastAPI, Pydantic v2, LangGraph, local Ollama (Llama 3)
- STT: faster-whisper
- Voice cloning TTS: Coqui XTTS (Linux/Docker runtime path)
- Frontend: AngularJS MVC (service/controller/view)
- Quality: pytest, mypy, ruff, pre-commit
- Delivery: Docker, Docker Compose, GitHub Actions CI/CD

## Runtime Flow

1. User uploads audio + selects genre + target minutes
2. Backend creates a job and runs a LangGraph pipeline
3. Pipeline steps:
   - transcribe audio
   - summarize transcript (genre-aware + target length)
   - extract speaker reference clip
   - synthesize summary voice with cloned timbre
4. UI polls job status and plays/downloads generated WAV

## Requirements

- Docker + Docker Compose
- Ollama installed locally on host (`http://host.docker.internal:11434` from containers)
- Sufficient CPU/RAM (GPU recommended for faster TTS)

## Quick Start (Docker)

1. Prepare environment:

```bash
cp .env.example .env
```

2. Pull Llama model (host-side, optional but recommended):

```bash
./scripts/bootstrap_ollama.sh llama3
```

3. Build app images:

```bash
docker build -f infra/docker/backend.Dockerfile -t voice-backend:test .
docker build -f infra/docker/frontend.Dockerfile -t voice-frontend:test .
```

4. Run stack (backend + frontend, host Ollama):

```bash
docker compose -f infra/docker/docker-compose.yml up -d --no-build backend frontend
```

Or via Makefile:

```bash
make compose-up
```

5. Optional: run bundled Ollama container profile:

```bash
docker compose -f infra/docker/docker-compose.yml --profile with-ollama up -d --no-build
```

6. Open UI:

- `http://localhost:8080`

7. Backend API:

- `http://localhost:8000/health`
- `http://localhost:8000/api/v1/jobs/genres`

## API

- `POST /api/v1/jobs` (multipart form):
  - `audio_file`: binary audio file
  - `genre`: `general|economical|social|technical|news`
  - `target_minutes`: integer
- `GET /api/v1/jobs/{job_id}`: job status and summary payload
- `GET /api/v1/jobs/{job_id}/audio`: generated summary WAV

## Local Development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pip install -e .[speech]
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Quality Commands

```bash
ruff check backend
ruff format --check backend
mypy backend/app backend/tests
pytest
npm --prefix frontend run lint
npm --prefix frontend run build
```

## Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```

## Notes

- Full voice cloning quality depends on source audio quality and language match.
- Coqui XTTS in non-interactive Docker runtime requires `COQUI_TOS_AGREED=1`.
- CPU-only XTTS synthesis is slow for long outputs; 1-minute summaries can take several minutes to render.
- For large workloads, replace in-memory job tracking with persistent DB + queue workers.
- Coqui TTS is configured as Linux runtime dependency; use Docker for consistent voice cloning setup.
