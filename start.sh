#!/bin/bash
cd resume-analyser-backend
exec gunicorn app:app
