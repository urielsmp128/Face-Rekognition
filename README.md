# Description

This project will work as an API for Photo AI, which uses the Python language together with Fast API to create REST services to be used as a means of communication.

# Deploy Locally

## Requirements

The following core prerequisites are necessary:

- Python installed (Recommended version: ≥ 3.11.3)
- PIP installed (Recomended version ≥ 23.1.2)

## Getting Started

Install dependencies:

```bash
pip -r requirements.txt
```

or

```bash
python3 -m pip -r requirements.txt
```

Run project:

```bash
uvicorn app.main:app --reload
```

Install pre-commit:

```bash
pre-commit install
```

# Deploy with Docker

## Requirements

The following core prerequisites are necessary:

- Docker installed (Recomended version ≥23.0.5)
- Docker Compose (Recomended version ≥ 2.17.3 )

## Getting Started

### Run Virtual Image

```bash
docker-compose --project-name photo-ai-api up -d
```

### Stop Virtual Image

```bash
docker stop $(docker ps -a -q)
```

or

```bash
docker stop <ID-Docker>
```

### Delete Virtual Image

```bash
docker rm $(docker ps -aq)
```

and

```bash
docker rmi $(docker images -a -q)
```

# Tests

Once deployed, the API will be available by default at http://127.0.0.1:8000/

Fast API provides us with a simple way as all the services we create will be documented and available at http://127.0.0.1:8000/docs

## Learn More

To learn more take a look at the following resources:

- [Python](https://www.python.org/downloads/release/python-3113/)
- [Fast API](https://fastapi.tiangolo.com/tutorial/)
- [Docker](https://docs.docker.com/engine/reference/run/)
