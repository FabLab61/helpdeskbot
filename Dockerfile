FROM debian:stable-slim

ARG bot_token
ARG chat_id
ARG redis_host=redis-support-bot
ARG redis_port=6379
ARG redis_db=0

ENV support_bot=/var/lib/support_bot

RUN mkdir $support_bot

COPY . $support_bot

WORKDIR $support_bot

RUN ./configure.sh && rm configure.sh

CMD $support_bot/startup
