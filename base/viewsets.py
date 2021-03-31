from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Moment, Survey, Log
from .serializers import MomentSerializer, MomentReadSerializer, UserSerializer, SurveySerializer, LogSerializer
from data.models import Dataset, Line
from data.serializers import LineSerializer
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Max
import csv, math
from rest_framework.mixins import UpdateModelMixin
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
    queryset = Moment.objects.filter(dataset = dataset, author__is_active = True)
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

    headers = ['username', 'condition', 'dataset', 'timestamp', 'speaker', 'line', 'direction', 'agree_cnt', 'exact_cnt', 'reason', 'possible_comment', 'created_at']

    writer.writerow(headers)

    for moment in Moment.objects.filter(dataset = dataset, author__is_active = True):
      agree_cnt = Moment.objects.filter(dataset = dataset, line = moment.line, direction = moment.direction, author__is_active = True, created_at__lt = moment.created_at).count()
      exact_cnt = Moment.objects.filter(dataset = dataset, line = moment.line, direction = moment.direction, author__is_active = True, created_at__lt = moment.created_at, reason = moment.reason).count()
      row = [moment.author.username, moment.author.first_name, moment.dataset.dataset_id, moment.line.starttime, moment.line.speaker, moment.line.text, moment.direction, agree_cnt, exact_cnt, moment.reason, moment.possible_comment, moment.created_at]
      writer.writerow(row)

    return response

  @action(detail = False, methods=['get'])
  def export_stats(self, request):
    datasets = Dataset.objects.all().order_by('dataset_id')

    result = {}

    for dataset in datasets:
      moments = Moment.objects.filter(author__is_active = True, dataset = dataset).order_by('timestamp')
      moments_count = moments.count()
      if moments_count == 0:
        continue
      count_lines = Line.objects.filter(dataset=dataset).count()
      script_length = Line.objects.filter(dataset=dataset).aggregate(Max('starttime'))['starttime__max']
      last_coverage = moments.last().timestamp
      three_q_coverage = moments[math.ceil(moments_count * 0.75)].timestamp
      result[dataset.dataset_id] = {
        'count_lines': count_lines,
        'script_length': script_length,
        'moments_count': moments_count,
        'last_coverage': last_coverage,
        'three_q_coverage': three_q_coverage
      }

    return Response(result)

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

    headers = ['username', 'time_spent_task', 'fas1', 'fas2', 'fas3', 'pus1', 'pus2', 'pus3', 'aes1', 'aes2', 'aes3', 'rws1', 'rws2', 'rws3', 'sanity_check', 'status', 'free_response', 'topic', 'created_at', 'num_pages']

    writer.writerow(headers)

    for survey in Survey.objects.filter(user__is_active = True):
      try:
        time_start_log = Log.objects.filter(user = survey.user, event_name='StartTask', created_at__lt = survey.created_at).order_by('-created_at')
        time_start = time_start_log[0].created_at
        time_end_log = Log.objects.filter(user = survey.user, event_name='EndTask', created_at__lt = survey.created_at).order_by('-created_at')
        time_end = time_end_log[0].created_at

        num_pages = Log.objects.filter(user = survey.user, event_name='SeeMore').count()

        time_spent = (time_end - time_start).total_seconds()
      except Exception as err:
        time_spent = 0
        num_pages = 0 

      row = [survey.user.username, time_spent, survey.fas1, survey.fas2 , survey.fas3, survey.pus1, survey.pus2 , survey.pus3, survey.aes1, survey.aes2 , survey.aes3, survey.rws1, survey.rws2, survey.rws3, (survey.sanity_check == 2), survey.user.first_name, survey.free_response, survey.topic, survey.created_at, num_pages]

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
      # token = Token.objects.get(user = user[0])
      # return Response(status = 200, data = {
      #   'token': token.key,
      #   'username': user[0].username,
      #   'turker_id': user[0].last_name

      # })

    else:
      serializer = UserSerializer(data = request.data)

      if serializer.is_valid():
        newUser = serializer.save()
        token = Token.objects.get(user = newUser)
        return Response(status = 201, data = {
          'token': token.key,
          'username': newUser.username,
          'turker_id': newUser.last_name
        })

      return Response(status = 400, data = serializer.errors)
    
class DeactivateUser(APIView):
  queryset = User.objects.all()

  def put(self, request):
    data = request.data

    succeeded_user = []
    try:
      for user_id in data:
        user = User.objects.get(username=user_id)
        user.is_active = False

        user.save()
        succeeded_user.append(user_id)
    except Exception as err:
      return Response(status = 400, data={'err': err, 'succeeded_user': succeeded_user})

    
    return Response(status = 200, data = succeeded_user)


    


