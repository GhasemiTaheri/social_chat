from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response


class SearchMixin:
    filter_backends = [filters.SearchFilter]

    @action(methods=['get'], detail=False)
    def search(self, request, *args, **kwargs):
        search = request.query_params.get('search', None)
        if search:
            return self.list(request, *args, **kwargs)

        return Response(data={'results': []}, status=200)
