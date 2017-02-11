#   This file is part of Support Bot.
#   Copyright (C) 2017  Sergey Sherkunov <leinlawun@openmailbox.org>
#
#   This Support Bot is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This Support Bot is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

FROM debian:stable-slim

ARG BOT=support_bot
ARG BOT_DIR=/var/lib/$BOT

ENV REDIS_HOST=redis-support-bot \
    REDIS_PORT=6379 \
    REDIS_DB=0 \
    BOT_TOKEN= \
    CHAT_ID=

RUN apt update && \
    apt install -y --no-install-recommends gettext python3-pip && \
    mkdir $BOT_DIR

COPY . $BOT_DIR

WORKDIR $BOT_DIR

RUN ./locale.sh && rm locale.sh

RUN pip3 install -r requirements.txt && rm requirements.txt

ENTRYPOINT ./support_bot.py
