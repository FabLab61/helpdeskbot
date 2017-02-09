#!/usr/bin/env bash

apt update && apt install -y --no-install-recommends gettext python3-pip || exit 1

pip3 install -r requirements.txt && rm requirements.txt || exit 1

for i in `ls locale`; do
  MESSAGES=locale/$i/LC_MESSAGES
  for j in `ls $MESSAGES`; do
    MESSAGE=$MESSAGES/$j
    msgfmt $MESSAGE -o ${MESSAGE%.*}.mo && rm $MESSAGE || exit 1
  done
done

if [[ -z $bot_token || -z $chat_id ]]; then
  exit 1
fi

sed 's/^token=$/&'"$bot_token"'/' -i config.ini
sed 's/^support_chat_id=$/&'"$chat_id"'/' -i config.ini

if [ -n $redis_host ]; then
  sed 's/^host=.*$/host='"$redis_host"'/g' -i config.ini
fi
if [ -n $redis_port ]; then
  sed 's/^port=.*$/port='"$redis_port"'/g' -i config.ini
fi
if [ -n $redis_db ]; then
  sed 's/^db=.*$/db='"$redis_db"'/g' -i config.ini
fi
