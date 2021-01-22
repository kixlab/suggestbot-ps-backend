from rest_framework import serializers
from .models import Line

class DataSetSerializer(serializers.Serializer):
  dataset_id = serializers.CharField()

class LineSerializer(serializers.ModelSerializer):
  dataset = serializers.StringRelatedField(read_only = True)
  moments = serializers.IntegerField(read_only=True)
  class Meta:
    model = Line
    fields = '__all__'