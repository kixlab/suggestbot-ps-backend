from django.db import models
from django.contrib.auth.models import User
from data.models import Dataset, Line
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
# Create your models here.


class Moment(models.Model):
  POSITIVE = 'POSITIVE'
  NEGATIVE = 'NEGATIVE'
  NEUTRAL = 'NEUTRAL'
  DIRECTION_CHOICES = [
    (POSITIVE, 'Positive'),
    (NEGATIVE, 'Negative'),
    (NEUTRAL, 'Neutral')
  ]

  author = models.ForeignKey(User, on_delete = models.CASCADE)
  dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
  line = models.ForeignKey(Line, on_delete = models.CASCADE, null=True)
  timestamp = models.FloatField()
  affected_speaker = models.CharField(max_length=15)
  direction = models.CharField(choices = DIRECTION_CHOICES, max_length=8, default = NEUTRAL)
  reason = models.TextField()

  possible_comment = models.TextField()
  possible_line = models.TextField(blank = True)

  created_at = models.DateTimeField(auto_now_add = True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return '%s: %s - %f' % (self.dataset.dataset_id, self.direction, self.timestamp)

@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance = None, created = False, **kwargs):
  if created:
    Token.objects.create(user = instance)


class Survey(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  # fas1 = models.IntegerField()
  # fas2 = models.IntegerField()
  # fas3 = models.IntegerField()

  pus1 = models.IntegerField()
  pus2 = models.IntegerField()
  pus3 = models.IntegerField()

  # aes1 = models.IntegerField()
  # aes2 = models.IntegerField()
  # aes3 = models.IntegerField()

  rws1 = models.IntegerField()
  rws2 = models.IntegerField()
  rws3 = models.IntegerField()

  sanity_check = models.IntegerField()
  status = models.CharField(max_length=20)

  created_at = models.DateTimeField(auto_now_add = True)
  updated_at = models.DateTimeField(auto_now=True)

