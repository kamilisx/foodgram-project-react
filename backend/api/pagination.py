from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination"""
    page_size: int = 6
    page_size_query_param: str = "limit"
    max_page_size: int = 20
