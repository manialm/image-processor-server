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

# Example commands
0. Install [httpie](https://httpie.io/)

1. Upload image:
```bash
http POST localhost:8000/upload --form file@image.png
```

2. Download image:
```bash
http --follow localhost:8000/get-processed-file?filename=dog.png > out.png
```