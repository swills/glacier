#!/bin/sh

export SLACK_API_TOKEN=$(vault kv get -field=oauth_access_token secret/freebsd/slack/swills_test_app)
export SLACK_BOT_TOKEN=$(vault kv get -field=user_authed_magic_token secret/freebsd/slack/swills_classic_slack_app)
./convert.sh
python glacier.py
