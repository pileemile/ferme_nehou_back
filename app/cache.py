from django.core.cache import cache
import hashlib
import json


def make_cache_key(prefix, params=None):
  """
  Génère une clé de cache unique basée sur le préfixe et les paramètres

  Exemple:
  make_cache_key('rooms_list', {'page': 1, 'page_size': 10})
  → 'rooms_list_a1b2c3d4'
  """
  if params:
    params_str = json.dumps(params, sort_keys=True)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
    return f"{prefix}_{params_hash}"
  return prefix


def cache_response(key, timeout, func, *args, **kwargs):
  """
  Helper pour mettre en cache le résultat d'une fonction

  Utilisation :
  data = cache_response('rooms_list', 300, get_rooms_data)
  """
  cached = cache.get(key)
  if cached is not None:
    return cached, True  # (data, from_cache)

  data = func(*args, **kwargs)
  cache.set(key, data, timeout)
  return data, False


def invalidate_room_cache(room_id=None):
  """Invalider le cache des chambres après modification"""
  # Supprimer le cache de la liste
  cache.delete_pattern('rooms_list_*')
  cache.delete_pattern('rooms_search_*')
  cache.delete_pattern('rooms_featured_*')

  # Si room_id, supprimer le cache de cette chambre
  if room_id:
    cache.delete(f'room_detail_{room_id}')


def invalidate_review_cache(room_id=None):
  """Invalider le cache des avis après modification"""
  cache.delete_pattern('reviews_recent_*')
  if room_id:
    cache.delete(f'room_detail_{room_id}')


def invalidate_stats_cache():
  """Invalider le cache des statistiques"""
  cache.delete_pattern('stats_*')
