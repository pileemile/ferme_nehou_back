import bleach


def sanitize_html(text, allowed_tags=None):
    """
    Nettoie le HTML pour prévenir les attaques XSS
    """
    if allowed_tags is None:
        allowed_tags = []

    return bleach.clean(
        text,
        tags=allowed_tags,
        strip=True
    )


def sanitize_text(text):
    """
    Nettoie le texte brut (pas de HTML du tout)
    """
    return bleach.clean(text, tags=[], strip=True)


def sanitize_rich_text(text):
    """
    Nettoie le HTML en autorisant quelques tags de base
    """
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li',
        'a', 'blockquote'
    ]

    allowed_attributes = {
        'a': ['href', 'title'],
    }

    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )