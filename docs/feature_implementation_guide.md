# PodcastAI Feature Implementation Steps

1. Create model file at `/api/models/{domain}.py` with SQLAlchemy models and `extend_existing=True`.
2. Update `/api/models/__init__.py` to import and re-export new models.
3. Create schema file at `/api/schemas/{domain}.py` with Pydantic request/response models.
4. Update `/api/schemas/__init__.py` to import and re-export new schemas.
5. Create router file at `/api/routers/{domain}.py` with FastAPI endpoints and authentication.
6. Update `/api/routers/__init__.py` to import and re-export new router.
7. Register router in `/api/main.py` with appropriate prefix.
8. Create test file at `/api/tests/test_{domain}.sh` sourcing common utilities from `common.sh`.
9. Update `/api/tests/run_tests.sh` to include new test file.
10. Create API documentation at `/docs/{domain}_api_endpoints.md`.
11. Update `/docs/database_structure.md` if new models are added.

## Commands

```bash
# Start API server
uvicorn api.main:app --host 0.0.0.0 --port 8011 --reload

# Run specific test
./api/tests/test_{domain}.sh

# Run all tests
./api/tests/run_tests.sh
```

## Guidelines

- Include request/response schemas for Swagger docs.
- Add proper authentication for protected endpoints.
- Follow established naming conventions.
- Write tests for all endpoints.
- Keep documentation updated.
- Never start API server in code.
- Make minimal changes that don't break existing functionality.
