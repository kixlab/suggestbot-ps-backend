from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Moment, Survey, Log
from .serializers import MomentSerializer, MomentReadSerializer, UserSerializer, SurveySerializer, LogSerializer
from data.models import Dataset, Line
from data.serializers import LineSerializer
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import csv
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

  @action(detail = False, methods=['get'])
  def export_csv(self, request):
    dataset_id = request.query_params['dataset']
    dataset = get_object_or_404(Dataset, dataset_id = dataset_id)
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=%s-moments.csv' % dataset_id
    writer = csv.writer(response)

    headers = ['username', 'dataset', 'timestamp', 'speaker', 'line', 'direction', 'reason', 'possible_comment', 'created_at']

    writer.writerow(headers)

    for moment in Moment.objects.filter(dataset = dataset):
      row = [moment.author.username, moment.dataset.dataset_id, moment.line.starttime, moment.line.speaker, moment.line.text, moment.direction, moment.reason, moment.possible_comment, moment.created_at]
      writer.writerow(row)

    return response

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

  @action(detail = False, methods=['get'])
  def export_csv(self, request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=surveys.csv'
    writer = csv.writer(response)

    headers = ['username', 'time_spent_task', 'pus1', 'pus2', 'pus3', 'rws1', 'rws2', 'rws3', 'sanity_check', 'status', 'free_response', 'created_at']

    writer.writerow(headers)

    for survey in Survey.objects.all():
      try:
        time_start_log = Log.objects.get(user = survey.user, event_name='StartTask')
        time_start = time_start_log.created_at
      except:
        time_start = 0
      try:
        time_end_log = Log.objects.get(user = survey.user, event_name='EndTask')
        time_end = time_end_log.created_at
      except:
        time_end =  0

      row = [survey.user.username, time_start - time_end, survey.pus1, survey.pus2 , survey.pus3, survey.rws1, survey.rws2, survey.rws3, (survey.sanity_check == 2), survey.status, survey.free_response, survey.created_at]

      writer.writerow(row)

    return response

class LogViewSet(viewsets.ModelViewSet):
  queryset = Log.objects.all()
  serializer_class = LogSerializer

  def create(self, request):
    data = request.data
    data['user'] = request.user.pk

    serializer = LogSerializer(data = data)

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
    


