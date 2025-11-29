# Quick Start: Excel Import

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Create Excel Template

```bash
python manage.py create_excel_template my_data.xlsx
```

This creates an Excel file with three sheets:
- **Users**: User accounts and fencer profiles
- **Events**: Tournaments and events
- **Participations**: Links fencers to events with results

## Step 3: Fill in Your Data

Open `my_data.xlsx` and fill in your data following the example rows.

**Important:**
- Keep the header row (first row) as is
- Fill in required fields (marked in instructions)
- Use consistent identifiers (username, email, or "first_name last_name")

## Step 4: Test Your Data (Recommended)

```bash
python manage.py import_from_excel my_data.xlsx --dry-run
```

This will show you what would be imported without actually saving anything.

## Step 5: Import Data

```bash
# If users don't exist yet, use --create-users
python manage.py import_from_excel my_data.xlsx --create-users
```

## That's It!

Check your data in Django admin: http://127.0.0.1:8000/admin/

For detailed instructions, see `EXCEL_IMPORT_INSTRUCTIONS.md`


