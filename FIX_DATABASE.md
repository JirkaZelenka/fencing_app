# Fix Database Tables Error

The migration file has been created. Now you need to apply it:

## Steps to Fix:

1. **Stop your Django server** (if it's running)
   - Press `Ctrl+C` in the terminal where the server is running

2. **Run the migration command:**
   ```bash
   python manage.py migrate
   ```

3. **Restart your server:**
   ```bash
   python manage.py runserver
   ```

## What this does:

The `migrate` command will:
- Read the migration file `fencers/migrations/0001_initial.py`
- Create all the database tables:
  - fencers_club
  - fencers_fencerprofile
  - fencers_tournament
  - fencers_tournamentparticipation
  - fencers_trainingnote
  - fencers_circuittraining
  - fencers_circuitsong
  - fencers_eventphoto
  - fencers_calendarevent
  - fencers_eventreaction
  - fencers_paymentstatus
  - fencers_glossaryterm
  - fencers_guidevideo
  - fencers_rulesdocument
  - fencers_equipmentitem
  - fencers_userequipment

After running `migrate`, all tables will be created and the error should be resolved!

