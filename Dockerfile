FROM python:3.12.9-bookworm

WORKDIR /app

COPY requirements.txt .
COPY src .

RUN pip install \
  --no-cache-dir \
  --root-user-action ignore \
  -r requirements.txt

CMD ["tail", "-f", "/dev/null"]
