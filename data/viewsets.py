from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import LineSerializer
from .models import Line, Dataset
from rest_framework.decorators import action
from django.db.models import Count, Q

class LineViewSet(viewsets.ViewSet):
  queryset = Line.objects.all()
  serializer = LineSerializer

  @action(detail=False, methods = ['get'])
  def get_dataset(self, request):
    dataset_id = request.query_params['dataset']
    print(dataset_id)
    dataset = Dataset.objects.get(dataset_id = dataset_id)
    queryset = Line.objects.filter(dataset = dataset).annotate(
      moments_positive=Count('moment', filter=Q(moment__direction = 'POSITIVE')),
      moments_negative=Count('moment', filter=Q(moment__direction = 'NEGATIVE'))
    )
    serializer = LineSerializer(queryset, many = True)
    return Response(serializer.data)

  # @action(detail=False, methods = ['get'])
  # def get_dataset_counts(self, request):
  #   dataset_id = request.query_params['dataset']
  #   dataset = Dataset.objects.get(dataset_id = dataset_id)
  #   queryset = Line.objects.filter(dataset = dataset).annotate(
  #     moments_positive=Count('moment', filter=Q(moment__direction = 'POSITIVE')),
  #     moments_negative=Count('moment', filter=Q(moment__direction = 'NEGATIVE'))
  #   )
  #   serializer = LineSerializer(queryset, many = True)
  #   return Response(serializer.data)

    
  