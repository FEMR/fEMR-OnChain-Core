#!/bin/bash
/opt/app/build.sh all
celery --app=femr_onchain worker --loglevel=info