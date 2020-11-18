from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Moment, Survey
from .serializers import MomentSerializer, MomentReadSerializer, UserSerializer, SurveySerializer
from data.models import Dataset, Line
from data.serializers import LineSerializer
from rest_framework.authtoken.models import Token

class MomentViewSet(viewsets.ModelViewSet):
  queryset = Moment.objects.all()
  serializer_class = MomentReadSerializer

  def create(self, request):
    # serializer_class = MomentSerializer
    data = request.data
    dataset = Dataset.objects.get(dataset_id = data['dataset'])
    data['dataset'] = dataset.pk
    data['author'] = request.user.pk

    serializer = MomentSerializer(data = data)

    if serializer.is_valid():
      newMoment = serializer.save()
      newSerialization = MomentReadSerializer(newMoment)
      return Response(status = 201, data = newSerialization.data)
    
    return Response(status = 400, data = serializer.errors)

  def list(self, request):
    dataset_id = request.query_params['dataset_id']
    dataset = Dataset.objects.get(dataset_id = dataset_id)
    queryset = Moment.objects.filter(dataset = dataset)
    if request.user is not None:
      queryset = queryset.filter(author = request.user)
    
    serializer = MomentReadSerializer(queryset, many = True)

    return Response(serializer.data)

class SurveyViewSet(viewsets.ModelViewSet):
  queryset = Survey.objects.all()
  serializer_class = SurveySerializer

  def create(self, request):
    data = request.data
    data['user'] = request.user.pk

    serializer = SurveySerializer(data = data)

    if serializer.is_valid():
      newSurvey = serializer.save()
      return Response(status = 201, data = serializer.data)

    return Response(status = 400, data = serializer.errors)

class CreateUser(generics.CreateAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer


  def create(self, request):
    data = request.data

    user = User.objects.filter(username=request.data['username'])

    if user.exists():
      return Response(status = 403, data='Selected user already exists')
      # token = Token.objects.get(user = user)
      # return Response(status = 200, data = {
      #   'token': token.key,
      #   'username': newUser.username
      # })

    else:
      serializer = UserSerializer(data = request.data)

      if serializer.is_valid():
        newUser = serializer.save()
        token = Token.objects.get(user = newUser)
        return Response(status = 201, data = {
          'token': token.key,
          'username': newUser.username
        })

      return Response(status = 400, data = serializer.errors)
    


