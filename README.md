# bot-Support

A support-bot application with a Python source tree, public assets, runtime instance data, and a `doc/` directory. The repository also contains an HTML page related to emotion extraction from a camera.

## Requirements and setup

Inspect the dependency and configuration files under `src/` before creating a Python virtual environment. Keep local databases, logs, and credentials outside commits.

## Run locally

The application entry point is located under `src/`. Use the project-specific launcher documented in `doc/`, or invoke the Python module described there after installing its dependencies.

## Repository layout

| Path | Responsibility |
| --- | --- |
| `src/` | Application source |
| `public/` | Public web assets |
| `doc/` | Existing documentation |
| `instance/` | Local runtime state |
| `logs/` | Runtime logs |

## Deployment notes

Configure authentication, logging, and data retention before deploying a support bot. Do not commit the local database, generated logs, or secrets.
