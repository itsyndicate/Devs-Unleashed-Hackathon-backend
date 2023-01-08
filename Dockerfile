ARG IMAGE_VERSION=python:3.11.1-alpine
ARG PLATFORM=linux/amd64

###########
# BUILDER #
###########

# pull official base image
FROM --platform=${PLATFORM} ${IMAGE_VERSION} as builder

# create the appropriate directories
ENV APP_HOME=/app/web
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy requirements.txt
ADD ./requirements.txt .

# install psycopg2 dependencies
RUN set -ex \
    && apk update \
    && apk add --no-cache --virtual .build-deps postgresql-dev gcc python3-dev \
    musl-dev zlib-dev jpeg-dev build-base libwebp-dev linux-headers\
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir -r requirements.txt \
    && runDeps="$(scanelf --needed --nobanner --recursive /env \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u)" \
    && apk add --virtual rundeps $runDeps

# copy project
COPY . .
ADD media media
ADD static static

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
