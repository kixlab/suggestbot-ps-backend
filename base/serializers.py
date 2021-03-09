from rest_framework import serializers
from .models import Moment, Survey, Log
from django.contrib.auth.models import User
from data.serializers import DataSetSerializer, LineSerializer
from data.models import Line

# class DataSetSerializer(serializers.Serializer):
#   # dataset_id = serializers.CharField()

class MomentSerializer(serializers.ModelSerializer):
  # dataset = serializers.StringRelatedField()
  # dataset = DataSetSerializer()
  class Meta:
    model = Moment
    fields = '__all__'

class MomentReadSerializer(serializers.ModelSerializer):
  # dataset = serializers.StringRelatedField()
  # dataset = DataSetSerializer()
  line = LineSerializer(read_only = True)
  class Meta:
    model = Moment
    fields = '__all__'

  def create(self, validated_data):
    line_id = validated_data.pop('line')
    line = Line.objects.get(pk = line_id)

    newMoment = Moment(line = line, **validated_data)
    newMoment.save()

    return newMoment

class SurveySerializer(serializers.ModelSerializer):
  class Meta:
    model = Survey
    fields = '__all__'
    
class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['username', 'password', 'first_name', 'last_name', 'email']

    extra_kwargs = {'password': {'write_only': True}}

  def create(self, validated_data):
    user = User(
        username=validated_data['username'],
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        email=validated_data['email']
    )
    user.set_password(validated_data['password'])
    user.save()
    return user

class LogSerializer(serializers.ModelSerializer):
  class Meta:
    model = Log
    fields = '__all__'