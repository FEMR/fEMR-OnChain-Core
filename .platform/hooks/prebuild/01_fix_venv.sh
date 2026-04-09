#!/bin/bash
set -e
VENV=$(ls -d /var/app/venv/staging-* 2>/dev/null | head -1)
if [ -d "$VENV/lib" ] && [ ! -L "$VENV/lib64" ]; then
  rm -rf $VENV/lib64
  ln -s $VENV/lib $VENV/lib64
fi
