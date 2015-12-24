#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
    from django.core.management import execute_from_command_line

    root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, root)

    execute_from_command_line(sys.argv)
