from rest_framework.pagination import PageNumberPagination


class BasePagination(PageNumberPagination):
    """
    自定义分页
    """
    # 默认每页显示的个数
    page_size = 5
    # 可以动态改变每页显示的个数
    page_size_query_param = 'page_size'
    # 页码参数
    page_query_param = 'page'
    # 最多能显示多少页
    max_page_size = 100
