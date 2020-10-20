FROM debian:buster
COPY . /app
RUN  apt-get update \
  && apt-get install -y wget \
  && apt-get install -y gnupg
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/buster-pgdg-main" |  tee /etc/apt/sources.list.d/pgdg.list
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc |  apt-key add -
RUN sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/debian/buster-main' > /etc/apt/sources.list.d/timescaledb.list"
RUN wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey |  apt-key add -
RUN apt-get install timescaledb-postgresql-12
RUN service postgresql start 
RUN psql -U postgres -h localhost
RUN \q
CMD startup.sh
