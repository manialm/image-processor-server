# image-processor-server
Image processing server built with with RabbitMQ, MinIO, and monitoring with cAdvisor, Prometheus and Grafana

# How to run
Run the containers with docker compose:
```bash
docker compose up -d
```

# Run with tests
```bash
TEST=1 docker compose up --build --attach api
```
