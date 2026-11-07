#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "church.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        raise

    if len(sys.argv) > 1 and sys.argv[1] == "createsuperuser":
        import django
        django.setup()

        from django.contrib.auth import get_user_model
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        if not username:
            raise RuntimeError("DJANGO_SUPERUSER_USERNAME is not set")

        if User.objects.filter(username=username).exists():
            print(f"Superuser '{username}' already exists. Skipping.")
            return

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
