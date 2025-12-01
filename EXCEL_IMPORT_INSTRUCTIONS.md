# Excel Import Instructions

This guide explains how to populate the database with Users, Events, and Event Participations from an Excel file.

## Prerequisites

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
   This will install `openpyxl` which is needed to read Excel files.

2. Make sure your Django project is set up and migrations are applied:
   ```bash
   python manage.py migrate
   ```

## Excel File Structure

Your Excel file must contain **three sheets** with the following names and columns:

### Sheet 1: "Users"

This sheet contains user and fencer profile information.

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| `username` | Optional* | Django username (for User model) | `john.doe` |
| `email` | Optional* | Email address (for User model) | `john@example.com` |
| `first_name` | Optional* | First name (for FencerProfile) | `John` |
| `last_name` | Optional* | Last name (for FencerProfile) | `Doe` |
| `club_name` | Optional | Name of the club (for FencerProfile) | `Fencing Club Prague` |
| `phone` | Optional | Phone number (for FencerProfile) | `+420123456789` |
| `gender` | Optional | Gender (M, Z, or Ž) (for FencerProfile) | `M` |
| `birth_year` | Optional | Year of birth (for FencerProfile) | `2000` |

*At least one of `username`, `email`, or both `first_name` and `last_name` must be provided.

**Notes:**
- **User model** (authentication): Only `username` and `email` are stored here. Admin status is managed separately.
- **FencerProfile model** (fencer data): `first_name`, `last_name`, `club_name`, `phone`, `gender`, and `birth_year` are stored in the FencerProfile, which is linked to the User via a 1:1 relationship.
- If a user with the same username or email already exists, it will be used (not duplicated).
- If `--create-users` flag is used and user doesn't exist, a new user will be created with only username and email.
- If username is missing but name is provided, username will be auto-generated.
- Clubs will be created automatically if they don't exist.

### Sheet 2: "Events"

This sheet contains event/tournament information.

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| `title` | **Yes** | Event title | `Czech Fencing Championship 2024` |
| `date` | **Yes** | Event date (date only, no time) | `2024-03-15` |
| `location` | Optional | Event location | `Prague Sports Hall` |
| `description` | Optional | Event description | `Annual championship...` |
| `event_type` | Optional | Type: `tournament`, `humanitarian`, or `other` | `tournament` |
| `gender` | Optional | Gender: `M`, `Z`, or `V` (all) | `V` |
| `participants_count` | **Required for tournament/humanitarian** | Number of participants (must be > 0) | `40` |
| `external_link` | Optional | External URL (e.g., czechfencing) | `https://...` |

**Date Format:**
- `YYYY-MM-DD` (e.g., `2024-03-15`) - date only, no time

**Event Types:**
- `tournament` or `turnaj` → Tournament
- `humanitarian` or `humanitární` → Humanitarian tournament
- `other` or `ostatní` → Other event (default)

**Gender Values:**
- `M` → Male
- `Z` or `Ž` → Female
- `V`, `Vše`, or `All` → All genders (default)

### Sheet 3: "Participations"

This sheet links fencers to events with their results.

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| `fencer_identifier` | **Yes** | Username, email, or "first_name last_name" | `john.doe` or `John Doe` |
| `event_title` | **Yes** | Title of the event | `Czech Fencing Championship 2024` |
| `date` | Optional | Event date (for matching) | `2024-03-15` |
| `position` | Optional | Final position/ranking | `5` |
| `wins` | Optional | Number of wins | `8` |
| `losses` | Optional | Number of losses | `3` |
| `touches_scored` | Optional | Touches scored | `45` |
| `touches_received` | Optional | Touches received | `32` |
| `points` | Optional | Points (float number) | `12.5` |

**Notes:**
- `fencer_identifier` must match a value from the Users sheet (username, email, or "first_name last_name").
- `event_title` must match exactly with a title from the Events sheet.
- If multiple events have the same title, use `date` to specify which one.
- If a participation already exists (same fencer + event), it will be skipped (not duplicated).

## Usage

### Basic Import

```bash
python manage.py import_from_excel path/to/your/file.xlsx
```

### Create Users Automatically

If users don't exist in the database, use the `--create-users` flag:

```bash
python manage.py import_from_excel path/to/your/file.xlsx --create-users
```

This will:
- Create new User accounts for users that don't exist (with username and email only)
- Auto-generate usernames if not provided
- Create email addresses if not provided (format: `username@example.com`)
- Create FencerProfile records with all fencer-specific data (name, club, phone, gender, birth_year)

### Dry Run (Test Without Saving)

To test your Excel file without actually importing data:

```bash
python manage.py import_from_excel path/to/your/file.xlsx --dry-run
```

This will:
- Validate your Excel file structure
- Show what would be imported
- Not save anything to the database

### Combined Options

```bash
python manage.py import_from_excel data.xlsx --create-users --dry-run
```

## Import Order

The script imports data in the correct dependency order:

1. **Users** → Creates User accounts (if `--create-users` is used)
2. **FencerProfiles** → Creates fencer profiles linked to users and clubs
3. **Events** → Creates events/tournaments
4. **EventParticipations** → Links fencers to events with results

## Example Excel File

See `example_import_data.xlsx` for a complete example, or use the template generator:

```bash
python manage.py create_excel_template output_file.xlsx
```

## Common Issues and Solutions

### Issue: "Excel file not found"
**Solution:** Check the file path. Use absolute path or relative path from project root.

### Issue: "Events sheet is required but not found"
**Solution:** Make sure your Excel file has a sheet named exactly "Events" (case-sensitive).

### Issue: "User not found: username"
**Solution:** 
- Use `--create-users` flag to create users automatically, OR
- Create users manually in Django admin first, OR
- Make sure the username/email in Participations sheet matches exactly with Users sheet

### Issue: "Event not found: Event Title"
**Solution:** 
- Make sure event title in Participations sheet matches exactly with Events sheet
- If multiple events have same title, include `start_date` in Participations sheet

### Issue: "Invalid date format"
**Solution:** Use format `YYYY-MM-DD` (e.g., `2024-03-15`) - date only, no time

### Issue: Duplicate key errors
**Solution:** The script handles duplicates automatically:
- Users: Uses existing user if found by username/email
- Events: Uses existing event if found by title+date
- Participations: Skips if fencer+event combination already exists

## Tips

1. **Always test first**: Use `--dry-run` to validate your data before importing
2. **Backup database**: Make a backup before importing large amounts of data
3. **Check data quality**: Ensure all required fields are filled and formats are correct
4. **Start small**: Test with a few rows first, then import the full dataset
5. **Use consistent identifiers**: Use the same identifier format (username, email, or name) throughout

## Verification

After importing, verify the data:

1. Check Django admin: `/admin/`
   - Users: `auth/user/`
   - Fencer Profiles: `fencers/fencerprofile/`
   - Events: `fencers/event/`
   - Participations: `fencers/eventparticipation/`

2. Or use Django shell:
   ```bash
   python manage.py shell
   ```
   ```python
   from fencers.models import FencerProfile, Event, EventParticipation
   print(f"Fencer Profiles: {FencerProfile.objects.count()}")
   print(f"Events: {Event.objects.count()}")
   print(f"Participations: {EventParticipation.objects.count()}")
   ```

## Support

If you encounter issues:
1. Check the error message carefully
2. Verify your Excel file structure matches the requirements
3. Use `--dry-run` to see what would happen
4. Check the console output for warnings and errors


