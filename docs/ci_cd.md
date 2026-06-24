# CI/CD

The repository includes two GitHub Actions workflows.

## CI

File: `.github/workflows/ci.yml`

Runs on pull requests, pushes to `main`, and manual dispatch.

Checks:

- Install package with development dependencies
- Ruff linting
- Mypy type checking
- Pytest test suite
- Coverage XML artifact generation

## Container Build

File: `.github/workflows/container.yml`

Runs on pull requests, pushes to `main`, tags, and manual dispatch.

Checks:

- Builds the Docker image
- Pushes to GitHub Container Registry only for `main` and tags

## Deployment Direction

No production cloud deployment target is hard-coded yet. The intended next step is:

1. Keep the core workflow as a library and CLI.
2. Add a FastAPI service around isolated conversion jobs.
3. Package the service as a container.
4. Deploy to the chosen platform with object storage for uploaded files and generated artifacts.

This keeps the project cloud-friendly without locking the team into AWS, Azure, GCP, Fly.io, Render, or Kubernetes before the app shape is proven.
