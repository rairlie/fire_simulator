# Dockerfile
FROM python:3.11-slim

WORKDIR /app

#COPY simulate_fire.py .

RUN pip install numpy matplotlib pandas xlsxwriter

CMD ["python", "simulate_fire.py"]
