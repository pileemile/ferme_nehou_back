from django.test import SimpleTestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from app.pagination import CustomPageNumberPagination


class CustomPageNumberPaginationTests(SimpleTestCase):
    def test_paginated_response_shape(self):
        request = Request(
            APIRequestFactory().get("/api/rooms/?page=1", HTTP_HOST="localhost:8080")
        )
        paginator = CustomPageNumberPagination()

        page = paginator.paginate_queryset(list(range(150)), request)
        response = paginator.get_paginated_response(page)

        self.assertEqual(
            response.data,
            {
                "pagination": {
                    "total_items": 150,
                    "total_pages": 15,
                    "current_page": 1,
                    "page_size": 10,
                    "has_next": True,
                    "has_previous": False,
                    "next": "http://localhost:8080/api/rooms/?page=2",
                    "previous": None,
                },
                "results": list(range(10)),
            },
        )
