# Setup Instructions

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd fencing_app
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment file**
   ```bash
   copy .env.example .env
   ```
   (On Linux/Mac: `cp .env.example .env`)
   
   Edit `.env` and set your `SECRET_KEY` (generate a random string for production).

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - Main app: http://127.0.0.1:8000/
    - Admin panel: http://127.0.0.1:8000/admin/

## Creating User Accounts

1. Log in to the admin panel at `/admin/`
2. Go to "Users" and click "Add user"
3. Create up to 20 user accounts
4. For each user, create a "Fencer Profile" and assign them to a club

## Setting Up Data

Through the admin panel, you can:
- Create clubs
- Add tournaments and tournament participations
- Upload event photos
- Add calendar events
- Create glossary terms
- Add guide videos
- Upload rules documents
- Add equipment items
- Set payment statuses for users

## Production Deployment

For public deployment:

1. **Set environment variables** (in `.env` or your hosting platform):
   ```
   DEBUG=False
   SECRET_KEY=<generate-a-strong-secret-key>
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Use a production database** (PostgreSQL recommended):
   - Update `DATABASES` in `settings.py`
   - Run migrations on the production database

3. **Set up static files serving**:
   - Configure your web server (nginx, Apache) to serve static files
   - Or use a service like WhiteNoise

4. **Security considerations**:
   - Use HTTPS (SSL/TLS)
   - Keep `DEBUG=False` in production
   - Use strong `SECRET_KEY`
   - Regularly update dependencies
   - Set up proper backup for database

5. **Recommended hosting platforms**:
   - Heroku
   - PythonAnywhere
   - DigitalOcean
   - AWS
   - Railway

## Features

- User authentication
- Dark mode toggle
- Tournament statistics
- Training notes
- Circuit training with audio
- Event photos gallery
- Calendar with reactions
- Payment status tracking
- Glossary and guides
- Equipment tracking

