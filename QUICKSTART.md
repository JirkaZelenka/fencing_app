# Quick Start Guide

## First Time Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   - Copy `env.example` to `.env`
   - Edit `.env` and set a `SECRET_KEY` (use a random string)

3. **Initialize database:**
   ```bash
   python manage.py migrate
   ```

4. **Create admin user:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the app:**
   - Login page: http://127.0.0.1:8000/login/
   - Admin: http://127.0.0.1:8000/admin/

## Creating Users

1. Go to admin panel: http://127.0.0.1:8000/admin/
2. Click "Users" → "Add user"
3. Fill in username and password
4. Save the user
5. Go to "Fencer Profiles" → "Add fencer profile"
6. Select the user and assign a club

## Key Features

- **O mně**: User profile with basic stats
- **Statistiky**: Individual and club tournament statistics
- **Tréninky**: Training notes and circuit training with audio
- **Fotky**: Event photo gallery
- **Kalendář**: Event calendar with reactions
- **Placení**: Payment status with QR code
- **Návody**: Glossary, videos, rules, equipment assembly guide
- **Vybavení**: Equipment tracking with purchase links

## Dark Mode

Click the moon/sun icon in the navigation bar to toggle dark mode. Your preference is saved in localStorage.

## Admin Features

Through the admin panel, you can manage:
- Users and fencer profiles
- Clubs
- Tournaments and participations
- Training notes
- Circuit trainings and songs
- Event photos
- Calendar events
- Payment statuses
- Glossary terms
- Guide videos
- Rules documents
- Equipment items

