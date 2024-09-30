# 
FROM python:3.10.11

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app /code/app

WORKDIR "/code/app"

#
RUN chmod +x run.sh

# 
CMD ["./run.sh"]