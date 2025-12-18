# Repository Guidelines

## Project Structure & Module Organization
- Root layout: `backend/` FastAPI prototype, `docs/` architecture notes, `scripts/` helper utilities, and `Readme.md` for the product overview.
- Backend modules: `backend/app/main.py` hosts FastAPI routes and the WebSocket stub; `schemas.py` defines Pydantic models; `storage.py` holds the in-memory store; `monitoring.py` runs ICMP checks.
- Tests live in `backend/tests/`; keep fixtures and helpers close to the features they exercise.

## Build, Test, and Development Commands
- Create and activate a venv (Windows PowerShell): `python -m venv .venv; .venv\Scripts\Activate.ps1`.
- Install deps: `pip install -r backend/requirements.txt`.
- Run the API locally (hot reload): `uvicorn backend.app.main:app --reload` from the repo root.
- Smoke the backend via tests: `./scripts/run_backend_tests.sh` (wraps venv + pytest) or `pytest backend/tests` inside an active venv.

## Coding Style & Naming Conventions
- Python 3 with 4-space indentation and type hints throughout; mirror the existing Pydantic schemas and FastAPI patterns when adding routes.
- Prefer small, pure functions; keep request/response validation in `schemas.py` and state changes in `storage.py`.
- Use descriptive snake_case for functions/variables and UpperCamelCase for Pydantic models.

## Testing Guidelines
- Test with pytest; name files `test_*.py` and functions `test_*`.
- Add unit tests alongside new endpoints or storage behaviors; mock external calls where possible and avoid network in tests.
- Aim for regression coverage on validation rules (404/400 paths) and happy-path payload shapes.

## Commit & Pull Request Guidelines
- Commit messages: short imperative summaries (e.g., "Add link validation"), optionally followed by a blank line and detail if needed.
- Keep PRs scoped: describe motivation, key changes, and testing performed; link to any tracking issue.
- Include screenshots or curl/httpie snippets when altering API behavior or payloads to help reviewers verify.

## Security & Configuration Tips
- The prototype uses an in-memory store and permissive CORS; do not deploy as-is. Add auth, durable storage, and restricted origins before production.
- ICMP checks shell out to `ping`; ensure paths and permissions are appropriate for your environment when expanding monitoring backends.
