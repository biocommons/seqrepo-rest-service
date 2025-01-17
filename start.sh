#!/bin/sh
source venv/bin/activate
export SEQREPO_FD_CACHE_MAXSIZE=10
nohup seqrepo-rest-service /data/seqrepo/2024-02-20/ 2>&1 &