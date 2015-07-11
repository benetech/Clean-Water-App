"""
Local settings for avina_app project.

Sensitive data should go here and this file should never be check in with
the source code.

See settings.py and local_settings.py.sample

Based on:
http://www.sparklewise.com/django-settings-for-production-and-development-best-practices/
"""

# Map from FormHub login names to corresponding API Tokens.
FH_API_TOKENS = {
    "cleanwater": "b4bbcc2be57b4ed1ed5ffbb4e71bafd85227a6dc",
}

FH_SERVER = 'http://54.86.146.199'

