from rest_framework import viewsets
from .serializers import TodoSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Todo

class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

@api_view(['GET'])
def health_check(request):
    return Response({
        "status": "healthy"
    })