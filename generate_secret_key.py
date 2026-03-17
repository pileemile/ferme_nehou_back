# generate_secret_key.py
from django.core.management.utils import get_random_secret_key

print("Nouvelle SECRET_KEY:")
print(get_random_secret_key())