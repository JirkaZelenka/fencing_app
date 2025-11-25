# How to Fix "no such table" Error

The error occurs because the database tables haven't been created yet. Follow these steps:

## Step 1: Make sure you're in the project directory
```bash
cd C:\Users\jirka\Documents\MyProjects\fencing_app
```

## Step 2: Activate your virtual environment (if you're using one)
If you created a virtual environment, activate it first:
```bash
venv\Scripts\activate
```

## Step 3: Install dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

## Step 4: Create migration files
```bash
python manage.py makemigrations
```

## Step 5: Apply migrations to create database tables
```bash
python manage.py migrate
```

## Step 6: Restart your Django server
```bash
python manage.py runserver
```

After running these commands, all database tables will be created and the error should be resolved.

