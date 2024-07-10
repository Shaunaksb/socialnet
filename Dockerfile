FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /snet

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /snet/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY .env /snet/
COPY . /snet//

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "socialnet.wsgi:application"]