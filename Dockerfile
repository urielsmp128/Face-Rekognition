FROM python:3.10-buster

COPY ./app /code/app
COPY ./.env /code/.env
COPY ./requirements.txt /code/requirements.txt

WORKDIR /code

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
