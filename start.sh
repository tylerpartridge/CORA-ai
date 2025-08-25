#!/bin/bash
cd /var/www/cora
export PYTHONPATH=/var/www/cora
uvicorn app:app --host 0.0.0.0 --port 8000

