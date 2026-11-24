#!/usr/bin/env python
"""Django's command-line utility for administrative tasks (root wrapper)."""
import os
import sys

def main():
    """Run administrative tasks."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chicken_project'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chicken_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Default to testing 'crispy' when bare 'test' is run
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        sys.argv.append('crispy')
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
