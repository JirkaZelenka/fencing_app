# Legacy auth_user table may still have NOT NULL first_name/last_name columns while
# the model omitted them; inserts then failed. Sync DB + model.

from django.db import migrations, models


def _auth_user_columns(schema_editor):
    with schema_editor.connection.cursor() as cursor:
        desc = schema_editor.connection.introspection.get_table_description(
            cursor, "auth_user"
        )
    return {col.name.lower() for col in desc}


def add_name_columns_if_missing(_apps, schema_editor):
    columns = _auth_user_columns(schema_editor)
    qn = schema_editor.connection.ops.quote_name
    table = qn("auth_user")
    if "first_name" not in columns:
        schema_editor.execute(
            f"ALTER TABLE {table} ADD COLUMN {qn('first_name')} varchar(150) NOT NULL DEFAULT ''"
        )
    if "last_name" not in columns:
        schema_editor.execute(
            f"ALTER TABLE {table} ADD COLUMN {qn('last_name')} varchar(150) NOT NULL DEFAULT ''"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("fencers", "0030_alter_user_managers_alter_user_groups_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    add_name_columns_if_missing,
                    migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="user",
                    name="first_name",
                    field=models.CharField(
                        blank=True,
                        default="",
                        max_length=150,
                        verbose_name="Jméno",
                    ),
                ),
                migrations.AddField(
                    model_name="user",
                    name="last_name",
                    field=models.CharField(
                        blank=True,
                        default="",
                        max_length=150,
                        verbose_name="Příjmení",
                    ),
                ),
            ],
        ),
    ]
