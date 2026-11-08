# AI Job Matcher

Compares a resume with a job description and, optionally, uses an LLM to explain the gaps and draft tailored bullets and a cover letter. Built to speed up my own job applications.

## What it does
- **Offline baseline (no API key):** extracts skills from both texts, reports matched and missing skills, and a bag-of-words cosine similarity
- **With OpenAI (`--llm`):** embeddings-based similarity, plus a structured JSON analysis (match score, strengths, gaps, suggested resume bullets)
- **Cover letter drafting (`--cover-letter`)** from the resume facts only
- **REST API** (FastAPI) so it can run as a small microservice in a container

## GenAI design choices
- Prompts live in `prompts.py` as reviewable templates
- Prompts instruct the model to use **only facts from the resume** and never invent skills or numbers (reduces hallucination)
- Prompts explicitly exclude protected attributes (age, gender, religion, caste, nationality) from the assessment
- The model replies in JSON and the parser tolerates code fences or extra text
- LLM and embedding clients are behind small interfaces, so tests run with fakes and no network

## Quick start
```bash
pip install -r requirements.txt
export PYTHONPATH=src

# offline
python -m jobmatch.cli --resume examples/sample_resume.txt --jd examples/sample_jd.txt

# with OpenAI
cp .env.example .env && export OPENAI_API_KEY=...
python -m jobmatch.cli --resume examples/sample_resume.txt --jd examples/sample_jd.txt --llm --cover-letter
```

## REST API
```bash
uvicorn jobmatch.api:app --app-dir src
curl -X POST localhost:8000/match -H 'content-type: application/json' \
  -d '{"resume": "...", "jd": "...", "use_llm": false}'
```

## Docker
```bash
docker build -t ai-job-matcher .
docker run -p 8000:8000 -e OPENAI_API_KEY=... ai-job-matcher
```

## Tests
```bash
pytest -q
```

## Responsible use
This is a drafting aid. A match score is not a hiring decision, and generated text must be reviewed and kept truthful before it is sent to anyone.

## Tech
Python, OpenAI API (chat + embeddings), prompt engineering, FastAPI, Docker, GitHub Actions, pytest
