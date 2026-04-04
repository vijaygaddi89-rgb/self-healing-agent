FROM python:3.11-slim

WORKDIR /sandbox

RUN pip install --no-cache-dir pytest

COPY runner.py .

RUN useradd -m sandboxuser
USER sandboxuser

CMD ["python", "runner.py"]