#!/usr/bin/env bash

for i in `ls locale`; do
  MESSAGES_DIR=locale/$i/LC_MESSAGES
  MESSAGES=$MESSAGES_DIR/$i.po
  COMPILED_MESSAGES=$MESSAGES_DIR/$BOT.mo
  msgfmt $MESSAGES -o $COMPILED_MESSAGES && rm $MESSAGES || exit 1
done
