FROM python:3.10-slim

ARG FAST_ENV

ENV FAST_ENV=${FAST_ENV} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

RUN mkdir /app
WORKDIR /app

COPY requirements.txt ./aggregator/setup.py ./

RUN pip install -e .

COPY . .
CMD ["uvicorn", "aggregator.main:app", "--host", "0.0.0.0", "--port", "80"]