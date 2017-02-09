FROM ubuntu

ARG bot_token
ARG chat_id
ARG redis_host=redis-support-bot
ARG redis_port=6379
ARG redis_db=0

ENV support_bot=/var/lib/support_bot

RUN apt update
RUN apt install -y gettext
RUN apt install -y python3-pip

RUN mkdir $support_bot

COPY locale $support_bot/locale
COPY config.ini $support_bot
COPY main.py $support_bot
COPY requirements.txt $support_bot

WORKDIR $support_bot

RUN for i in `ls locale`; do MESSAGES=locale/$i/LC_MESSAGES; for j in `ls $MESSAGES`; do MESSAGE=$MESSAGES/$j; msgfmt $MESSAGE -o ${MESSAGE%.*}.mo; rm $MESSAGE; done; done

RUN if [ -z $bot_token ]; then exit 1; else sed 's/^token=$/&'"${bot_token}"'/' -i config.ini; fi;
RUN if [ -z $chat_id ]; then exit 1; else sed 's/^support_chat_id=$/&'"${chat_id}"'/' -i config.ini; fi;
RUN if [ -n $redis_host ]; then sed 's/^host=.*$/host='"$redis_host"'/g' -i config.ini; fi;
RUN if [ -n $redis_port ]; then sed 's/^port=.*$/port='"$redis_port"'/g' -i config.ini; fi;
RUN if [ -n $redis_db ]; then sed 's/^db=.*$/db='"$redis_db"'/g' -i config.ini; fi;

RUN pip3 install -r requirements.txt && rm requirements.txt

RUN (echo '#!/usr/bin/env python3' && echo 'from main import updater' && echo 'updater.start_polling()') > startup
RUN chmod a+x startup

ENTRYPOINT $support_bot/startup
