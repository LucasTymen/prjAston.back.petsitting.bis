# Job Search Agent — déploiement Contabo (Playwright + Cron)
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    cron curl wget gnupg \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 libpango-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY . .

RUN mkdir -p /app/storage /app/logs /app/resources
RUN echo "0 */2 * * * root cd /app && python -m scheduler.cron_runner --mode both --sources wttj,francetravail,indeed,hellowork,dogfinance,meteojob,glassdoor,linkedin,apec --max 10 >> /app/logs/cron.log 2>&1" > /etc/cron.d/job_agent && \
    echo "0 8 * * * root cd /app && python -m scheduler.followup_runner >> /app/logs/followup.log 2>&1" >> /etc/cron.d/job_agent && \
    chmod 0644 /etc/cron.d/job_agent

CMD ["cron", "-f"]
