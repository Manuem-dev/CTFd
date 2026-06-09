#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser if environment variables are provided
python manage.py createsuperuser_if_none_exists
echo "super user created successfully"

# Integration of supabase AI-agent( juste pour le test )
# echo "Adding supabase AI-Agent"
# npx skills add supabase/agent-skills
# echo "AI-Agent added successfully"

