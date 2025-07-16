# image-processor-server
Image processing server built with with RabbitMQ, MinIO, and monitoring with cAdvisor, Prometheus and Grafana

# How to run
Run the containers with docker compose:
```bash
docker compose up -d
```

Run the worker:
```bash
docker exec -it fastapi-app uv run -- python -m app.worker
```
