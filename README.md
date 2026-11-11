# AI Job Matcher

Compares a resume with a job description and, optionally, uses an LLM to explain the gaps and draft tailored bullets and a cover letter. Built to speed up my own job applications.

## What it does

- **Offline baseline (no API key):** extracts skills from both texts, reports matched and missing skills, and a bag-of-words cosine similarity.
- **With OpenAI (`--llm`):** embeddings-based similarity, plus a structured JSON analysis (match score, strengths, gaps, suggested resume bullets).
- **Cover letter drafting (`--cover-letter`)** from the resume facts only.
- **REST API** (FastAPI) so it can run as a small microservice in a container.

## Project layout

```
src/jobmatch/   api.py (FastAPI), cli.py, service.py, matcher.py, llm.py,
                prompts.py, skills.py, text.py, config.py
examples/       sample resume and job description
tests/          pytest tests (fake LLM and embedding clients, no network)
Dockerfile      container image (reads PORT, default 8000)
.github/        CI: tests + Docker build
```

## GenAI design choices

- Prompts live in `prompts.py` as reviewable templates.
- Prompts tell the model to use **only facts from the resume** and never invent skills or numbers (reduces hallucination).
- Prompts explicitly exclude protected attributes (age, gender, religion, caste, nationality) from the assessment.
- Resume and JD text are treated as untrusted data inside the prompt (basic prompt-injection hygiene).
- The model replies in JSON; the parser tolerates code fences or extra text and the score is clamped to 0-100.
- LLM and embedding clients sit behind small interfaces, so tests run with fakes and no network.
- Configuration comes from environment variables (12-factor); inputs are capped at 20,000 characters.

## Quick start

```bash
pip install -r requirements-dev.txt
export PYTHONPATH=src

# offline
python -m jobmatch.cli --resume examples/sample_resume.txt --jd examples/sample_jd.txt

# with OpenAI
cp .env.example .env      # then put your key in .env
python -m jobmatch.cli --resume examples/sample_resume.txt --jd examples/sample_jd.txt --llm --cover-letter
```

## REST API

```bash
uvicorn jobmatch.api:app --app-dir src
curl -X POST localhost:8000/match -H 'content-type: application/json' \
  -d '{"resume": "python docker", "jd": "python kubernetes", "use_llm": false}'
```

Endpoints: `GET /health`, `POST /match` (fields: `resume`, `jd`, `use_llm`, `cover_letter`).

## Docker

```bash
docker build -t ai-job-matcher .
docker run -p 8000:8000 -e OPENAI_API_KEY=... ai-job-matcher
```

## Deploy to Google Cloud Run

The container reads `PORT` (12-factor), so it runs on Cloud Run without changes. These are the commands, not a live deployment:

```bash
# offline mode only (no API key, so use_llm=true returns 503)
gcloud run deploy ai-job-matcher --source . --region asia-south1 --allow-unauthenticated

# with LLM mode: keep the key in Secret Manager and require authentication
gcloud run deploy ai-job-matcher --source . --region asia-south1 \
  --set-secrets OPENAI_API_KEY=openai-key:latest --no-allow-unauthenticated
```

Do not combine an API key with `--allow-unauthenticated`: anyone with the URL could spend your OpenAI credit.

## Tests

```bash
pytest -q
```

## Limitations / next steps

- The skill list in `skills.py` is hand-written and covers common tech skills only.
- The offline score is a heuristic (70% skill coverage, 30% text similarity), not a validated model.
- No evaluation set yet to measure how well scores match human judgement.
- Next: load skills from a config file, add PDF resume input, add a small evaluation set.

## Responsible use

This is a drafting aid. A match score is not a hiring decision, and generated text must be reviewed and kept truthful before it is sent to anyone.

## Tech

Python, OpenAI API (chat + embeddings), prompt engineering, FastAPI, Docker, GitHub Actions, pytest
