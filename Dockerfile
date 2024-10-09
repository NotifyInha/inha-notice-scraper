# 
FROM python:3.10.11

# 
WORKDIR /code

# install lib
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# cron setting
# RUN apt-get update && apt-get install -y cron

# COPY crontab /etc/cron.d/crawler-cron

# RUN chmod 0644 /etc/cron.d/crawler-cron

# RUN crontab /etc/cron.d/crawler-cron

# code setting
COPY ./app /code/app

WORKDIR "/code/app"

RUN chmod +x run.sh

# run
CMD ["./run.sh"]