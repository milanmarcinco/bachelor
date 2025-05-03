FROM python:3.9-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install \
  --no-cache-dir \
  --root-user-action ignore \
  -r requirements.txt

CMD ["echo", "Specify a command to run!"]
