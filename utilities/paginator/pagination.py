from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from rest_framework.settings import api_settings


class MessagePagination(BasePagination):
    page_size = api_settings.PAGE_SIZE
    page_query_param = 'last_message_id'

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        last_message = self.get_last_message_id(request)

        if int(last_message) == 0:
            return list(queryset[:self.page_size])

        return list(queryset.filter(id__lt=last_message)[:self.page_size])

    def get_paginated_response(self, data):
        return Response({
            'results': data
        })

    def get_last_message_id(self, request):
        return request.query_params.get(self.page_query_param, 0)
