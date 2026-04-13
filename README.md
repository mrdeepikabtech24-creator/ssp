# Smart Student Planner (SSP)

## Overview

Smart Student Planner (SSP) is a full-stack academic management web application built with Flask and SQLite. It helps students organize their coursework by providing adaptive timetable generation, task tracking, and a visual analytics dashboard — all in one place.

The adaptive timetable engine analyzes each task's deadline, difficulty, and estimated hours to generate a balanced weekly study schedule. It automatically inserts break slots every 90 minutes and avoids scheduling outside the 7 AM–10 PM window, ensuring a realistic and sustainable study plan.

SSP follows Agile (Scrum/Kanban) development methodology and is fully containerized with Docker, deployable via Docker Compose or Kubernetes, and includes a complete CI/CD pipeline powered by GitHub Actions.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.x |
| Database | SQLite (via SQLAlchemy ORM) |
| Authentication | Flask-Login, Werkzeug password hashing |
| Forms | Flask-WTF, WTForms |
| Frontend | HTML5, Bootstrap 5, Chart.js |
| Testing | pytest, Flask test client |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes (k8s) |
| CI/CD | GitHub Actions |
| Web Server | Gunicorn (production), Nginx (reverse proxy) |

## Architecture

The application is organized as a Flask application factory with four blueprints:

- `auth` — Registration, login, logout with session management
- `tasks` — Full CRUD for academic tasks with priority/status tracking
- `timetable` — Adaptive schedule generation via `TimetableGenerator` algorithm
- `analytics` — REST API endpoints feeding Chart.js dashboard visualizations

## Getting Started

### Prerequisites

- Python 3.11+
- pip
- (Optional) Docker & Docker Compose

### Installation

```bash
git clone https://github.com/youruser/ssp.git
cd ssp
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Edit SECRET_KEY
flask run
```

Visit `http://localhost:5000`

### Docker Setup

```bash
cp .env.example .env
docker-compose up --build
```

Visit `http://localhost:80`

## Running Tests

```bash
pytest tests/ --verbose --tb=short
```

## CI/CD Pipeline

Two GitHub Actions workflows are included:

- `ci.yml` — Triggered on push/PR to `main` and `develop`. Runs pytest, flake8 linting, and a Docker build verification.
- `deploy.yml` — Triggered on push to `main` only. Builds and pushes the Docker image to Docker Hub, then runs a deployment step (customize with your server SSH commands).

Set the following GitHub repository secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD`.

## Kubernetes Deployment

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

Create required secrets and config maps before deploying:

```bash
kubectl create secret generic ssp-secrets --from-literal=secret-key=your-secret-key
kubectl create configmap ssp-config --from-literal=database-url=sqlite:///ssp.db
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Landing page |
| GET/POST | `/auth/register` | User registration |
| GET/POST | `/auth/login` | User login |
| GET | `/auth/logout` | User logout |
| GET | `/tasks/` | List all tasks |
| GET/POST | `/tasks/create` | Create new task |
| GET/POST | `/tasks/<id>/edit` | Edit task |
| POST | `/tasks/<id>/delete` | Delete task |
| POST | `/tasks/<id>/complete` | Mark task complete |
| GET | `/tasks/api/list` | JSON task list |
| GET | `/timetable/` | View weekly timetable |
| POST | `/timetable/generate` | Generate timetable |
| GET | `/timetable/api/slots` | JSON timetable slots |
| POST | `/timetable/clear` | Clear all slots |
| GET | `/analytics/` | Analytics dashboard |
| GET | `/analytics/api/summary` | Task summary stats |
| GET | `/analytics/api/weekly_progress` | 7-day completion data |
| GET | `/analytics/api/subject_breakdown` | Hours per subject |
| GET | `/analytics/api/streak` | Study streak count |
| GET | `/health` | Health check |

## Agile Methodology

SSP is developed using Agile Scrum with 1-week sprints. A Kanban board tracks work items across Backlog → In Progress → Review → Done columns. Each sprint delivers a working increment: Sprint 1 covered auth and models, Sprint 2 tasks and timetable, Sprint 3 analytics and DevOps.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request against `develop`
