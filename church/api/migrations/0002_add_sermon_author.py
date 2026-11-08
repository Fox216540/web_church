# Rename the legacy misspelled field while preserving existing sermon authors.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="sermon",
            old_name="autor",
            new_name="author",
        ),
    ]
