# ECAD Wrappers

Wrappers are thin ECAD-tool integrations. They should not contain the intelligence layer.

Each wrapper should:

- read the current project from the host ECAD tool
- send files or an internal model to the backend
- display copilot responses and validation warnings
- apply only user-approved changes
- run backend commands such as review, conversion, and simulation helper tasks

The backend owns parsing, validation, AI orchestration, simulation, prediction, and export logic.
