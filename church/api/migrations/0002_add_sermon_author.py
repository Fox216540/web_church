# Rename the legacy misspelled field while preserving existing sermon authors.

from django.db import migrations


def create_missing_initial_tables(apps, schema_editor):
    """Repair databases where 0001 was marked applied without its tables."""
    existing_tables = set(schema_editor.connection.introspection.table_names())

    for model_name in ("Event", "Sermon"):
        model = apps.get_model("api", model_name)
        if model._meta.db_table not in existing_tables:
            schema_editor.create_model(model)
            existing_tables.add(model._meta.db_table)


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_missing_initial_tables, migrations.RunPython.noop),
        migrations.RenameField(
            model_name="sermon",
            old_name="autor",
            new_name="author",
        ),
    ]
