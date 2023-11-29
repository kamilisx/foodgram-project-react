from rest_framework.pagination import PageNumberPagination

PAGE_SIZE = 6
MAX_PAGE_SIZE = 20


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination"""

    page_size = PAGE_SIZE
    page_size_query_param = "limit"
    max_page_size = MAX_PAGE_SIZE
