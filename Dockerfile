FROM python

COPY . /django

WORKDIR /django

EXPOSE 8000

RUN pip install -r req.txt

CMD uvicorn config.asgi:application --host 0.0.0.0




