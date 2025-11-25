#!/bin/bash
echo "Creating database migrations..."
python manage.py makemigrations
echo ""
echo "Applying migrations to create database tables..."
python manage.py migrate
echo ""
echo "Database setup complete!"
echo "You can now start the server with: python manage.py runserver"

