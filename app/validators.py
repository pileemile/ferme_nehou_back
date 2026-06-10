import re
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    cleaned = re.sub(r'[\s\-\.]', '', value)

    pattern = r'^(?:(?:\+|00)33|0)[1-9](?:[0-9]{8})$'

    if not re.match(pattern, cleaned):
        raise ValidationError(
            _('%(value)s n\'est pas un numéro de téléphone français valide'),
            params={'value': value},
        )


def validate_price(value):
    if value <= 0:
        raise ValidationError(
            _('Le prix doit être supérieur à 0'),
            params={'value': value},
        )


def validate_rating(value):
    if not 1 <= value <= 5:
        raise ValidationError(
            _('La note doit être entre 1 et 5'),
            params={'value': value},
        )


def validate_capacity(value):
    if value <= 0:
        raise ValidationError('La capacité doit être supérieure à 0')
    if value > 50:
        raise ValidationError('La capacité ne peut pas dépasser 50 personnes')


def validate_no_special_chars(value):
    if re.search(r'[<>\"\'&]', value):
        raise ValidationError(
            'Les caractères spéciaux < > " \' & ne sont pas autorisés'
        )


def validate_alphanumeric_spaces(value):
    if not re.match(r'^[a-zA-Z0-9\s\-\'àâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]+$', value):
        raise ValidationError(
            'Seuls les lettres, chiffres, espaces et tirets sont autorisés'
        )