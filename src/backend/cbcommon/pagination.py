from rest_framework import pagination


class RemovablePagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'

    def get_page_size(self, request):
        """ Disable pagination by 'listening' for a zero value for page_size_query_param """
        if self.page_size_query_param:
            try:
                return pagination._positive_int(
                    request.query_params[self.page_size_query_param], strict=False, cutoff=self.max_page_size)
            except (KeyError, ValueError):
                pass

        return self.page_size
