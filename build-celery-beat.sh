#!/bin/bash
/opt/app/build.sh all
celery --app=femr_onchain beat --loglevel=info