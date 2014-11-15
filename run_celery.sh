#!/bin/bash
celery worker -l info -P gevent -A grindstone.celery
