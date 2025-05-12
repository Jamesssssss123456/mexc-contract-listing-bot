FROM python:3.11-slim

RUN apt-get update && apt-get install -y wget gnupg curl ca-certificates fonts-liberation libnss3 libatk1.0-0     libatk-bridge2.0-0 libcups2 libxss1 libxcomposite1 libxrandr2 libxdamage1 libgbm1 libasound2 libxshmfence1 libx11-xcb1     libgtk-3-0 libxext6 libxfixes3 libglib2.0-0 libdrm2 &&     rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN python -m playwright install --with-deps

COPY main.py main.py

CMD ["python", "main.py"]
