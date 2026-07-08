from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
  """
  Pagination personnalisée avec métadonnées supplémentaires

  Paramètres URL :
  - page : numéro de page (défaut: 1)
  - page_size : taille de page (défaut: 10, max: 100)

  Exemple : GET /api/rooms/?page=2&page_size=5
  """
  page_size = 10
  page_size_query_param = 'page_size'  # Permettre de changer via URL
  max_page_size = 100
  page_query_param = 'page'

  def get_paginated_response(self, data):
    return Response({
      'pagination': {
        'total_items': self.page.paginator.count,
        'total_pages': self.page.paginator.num_pages,
        'current_page': self.page.number,
        'page_size': self.get_page_size(self.request),
        'has_next': self.page.has_next(),
        'has_previous': self.page.has_previous(),
        'next': self.get_next_link(),
        'previous': self.get_previous_link(),
      },
      'results': data
    })

  def get_paginated_response_schema(self, schema):
    return {
      'type': 'object',
      'properties': {
        'pagination': {
          'type': 'object',
          'properties': {
            'total_items': {'type': 'integer'},
            'total_pages': {'type': 'integer'},
            'current_page': {'type': 'integer'},
            'page_size': {'type': 'integer'},
            'has_next': {'type': 'boolean'},
            'has_previous': {'type': 'boolean'},
            'next': {'type': 'string', 'nullable': True},
            'previous': {'type': 'string', 'nullable': True},
          }
        },
        'results': schema,
      }
    }


class LargeResultsSetPagination(PageNumberPagination):
  """Pagination pour les grandes listes (ex: stats, photos)"""
  page_size = 50
  page_size_query_param = 'page_size'
  max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
  """Pagination pour les petites listes (ex: featured, recent)"""
  page_size = 5
  page_size_query_param = 'page_size'
  max_page_size = 20
