# pull official base image
FROM postgres:9.6-alpine

# run create.sql on init
ADD create-db-v3.sh /docker-entrypoint-initdb.d
