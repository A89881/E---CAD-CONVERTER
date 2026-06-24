# Cloud Readiness

The scaffold is designed to move cleanly from local development to cloud development later.

## Current Cloud-Friendly Pieces

- `Dockerfile` for repeatable runtime packaging
- `docker-compose.yml` for local container execution
- `.devcontainer/devcontainer.json` for consistent development environments
- `.env.example` for explicit runtime configuration
- CI workflow for tests and static checks
- Container workflow for registry-ready builds
- Local file storage abstraction through environment variables

## Recommended Future Runtime

```text
Browser or API client
        |
        v
FastAPI service
        |
        v
Job workspace per upload
        |
        v
Importer / validator / exporter pipeline
        |
        v
Object storage artifacts
        |
        v
Report and download links
```

## Future Cloud Services

- Object storage for uploaded ECAD projects and generated outputs
- PostgreSQL for projects, jobs, users, and audit trail
- Queue worker for long conversions
- Optional vector database for datasheets and documentation retrieval
- Secret manager for AI provider keys

## Operational Rules

- Treat uploaded ECAD archives as untrusted input.
- Never let AI silently modify output without validation.
- Store validation reports with every conversion.
- Keep conversion jobs reproducible from source artifact, version, and config.
