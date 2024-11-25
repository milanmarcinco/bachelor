FROM postgres

RUN apt-get update && \
    apt-get install -y postgresql-contrib && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 5432
