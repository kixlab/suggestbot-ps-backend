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
from django.db.models import Max, Count, Min, Q
import csv, math
from rest_framework.mixins import UpdateModelMixin
from django.utils import timezone
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
      # surveys = Survey.objects.filter(user__username__includes = dataset.dataset_id).annotate(time_coverage = int(user__username.split('-')[-1]) + 1)
      inner_qs = moments.values('line').distinct()
      all_lines = Line.objects.filter(dataset = dataset).order_by('starttime')
      lines = Line.objects.filter(id__in=inner_qs).order_by('starttime')
      lines_count = lines.count()
      if moments_count == 0:
        continue
      count_lines = all_lines.count()
      script_length = all_lines.aggregate(Max('starttime'))['starttime__max']
      last_coverage = moments.last().timestamp
      three_q_coverage = moments[math.ceil(moments_count * 0.75) - 1].timestamp
      three_q_line_num = moments[math.ceil(moments_count * 0.75) - 1].line.pk - all_lines.first().pk + 1
      three_q_line = lines[math.ceil(lines_count * 0.75) - 1].starttime
      three_q_line_linenum = lines[math.ceil(lines_count * 0.75) - 1].pk - all_lines.first().pk + 1
      three_q_annotation_density = moments.filter(line__pk__lte = lines[math.ceil(lines_count * 0.75) - 1].pk).count() / three_q_line_linenum 
      one_q_annotation_density = moments.filter(line__pk__gt = lines[math.ceil(lines_count * 0.75) - 1].pk).count() / (count_lines - three_q_line_linenum)

      three_q_distinct_density = lines.filter(pk__lte = lines[math.ceil(lines_count * 0.75) - 1].pk).count() / three_q_line_linenum 
      one_q_distinct_density = lines.filter(pk__gt = lines[math.ceil(lines_count * 0.75) - 1].pk).count() / (count_lines - three_q_line_linenum)
      result[dataset.dataset_id] = {
        'count_lines': count_lines,
        'script_length': script_length,
        'moments_count': moments_count,
        'last_coverage': last_coverage,
        'three_q_coverage': three_q_coverage,
        'three_q_line_num': three_q_line_num,
        'three_q_line': three_q_line,
        'three_q_line_linenum': three_q_line_linenum,
        'three_q_annotation_density': three_q_annotation_density,
        'one_q_annotation_density': one_q_annotation_density,
        'three_q_distinct_density': three_q_distinct_density,
        'one_q_distinct_density': one_q_distinct_density
      }

    return Response(result)

  @action(detail = False, methods = ['put'])
  def deduplicate(self, request):
    unique_fields = ['author', 'line', 'direction', 'possible_comment']
    duplicates = (
      Moment.objects.values(*unique_fields)
      .order_by()
      .annotate(min_id=Min('id'), count_id=Count('id'))
      .filter(count_id__gt=1)
    )

    count = 0
    for duplicate in duplicates:
      num_deletes = (
        Moment.objects.filter(**{x: duplicate[x] for x in unique_fields})
        .exclude(id=duplicate['min_id'])
        .delete()
      )
      count += num_deletes[0]


    return Response(count)

  @action(detail = False, methods = ['get'])
  def compute_bonus(self, request):
    users = User.objects.filter(is_active = True)
    if len(request.query_params) > 0:
      batch_name = request.query_params['batch_name']
      if batch_name == 'NA':
        users = user.exclude(username__contains='-')
      else:
        users = users.filter(username__endswith = batch_name)
    
    bonus = {}

    for user in users:
      parsing = user.username.split('-', 1)
      username = parsing[0]
      if len(parsing) == 2:
        postfix = parsing
      else:
        postfix = None
      moments = Moment.objects.filter(author = user)
      moments_count = moments.count()

      if moments_count < 5:
        continue

      bonus_quals = 0

      for moment in moments:
        agree_temp = Moment.objects.filter(direction = moment.direction, line = moment.line, author__is_active = True)
        if postfix is not None:
          agree_cnt = agree_temp.filter(Q(author__username__endswith = postfix) | Q(created_at__lte = moment.created_at)).count()
        else:
          agree_cnt = agree_temp.filter(created_at__lte = moment.created_at + timezone.timedelta(days=1)).count()
        if agree_cnt >= 3:
          bonus_quals += 1
      
      if bonus_quals > 0:
        bonus[user.username] = {
          'username': user.username,
          'user_created_at': user.date_joined,
          'bonus_count': min(moments_count - 5, bonus_quals),
          'moments_count': moments_count,
          'bonus_qualifying_moments': bonus_quals,
        }



    
    return Response(bonus)

    

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

  @action(detail = False, methods = ['put'])
  def deduplicate(self, request):
    unique_fields = ['user', 'free_response', 'topic']
    duplicates = (
      Survey.objects.values(*unique_fields)
      .order_by()
      .annotate(min_id=Min('id'), count_id=Count('id'))
      .filter(count_id__gt=1)
    )

    count = 0
    for duplicate in duplicates:
      num_deletes = (
        Survey.objects.filter(**{x: duplicate[x] for x in unique_fields})
        .exclude(id=duplicate['min_id'])
        .delete()
      )
      count += num_deletes[0]


    return Response(count)

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

        free_response = survey.free_response.replace('\n', ' ')
        topic = survey.topic.replace('\n', ' ')
      except Exception as err:
        time_spent = 0
        num_pages = 0 

      row = [survey.user.username, time_spent, survey.fas1, survey.fas2 , survey.fas3, survey.pus1, survey.pus2 , survey.pus3, survey.aes1, survey.aes2 , survey.aes3, survey.rws1, survey.rws2, survey.rws3, (survey.sanity_check == 2), survey.user.first_name, free_response, topic, survey.created_at, num_pages]

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


    


