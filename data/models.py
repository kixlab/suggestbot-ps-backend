from django.db import models

# Create your models here.

class Dataset(models.Model):
  dataset_id = models.CharField(max_length=15, unique=True)

  def __str__(self):
    return self.dataset_id


class Line(models.Model):
  dataset = models.ForeignKey(Dataset, on_delete = models.CASCADE)
  speaker = models.CharField( max_length=15)
  text = models.TextField()
  starttime = models.FloatField()
  endtime = models.FloatField()

  def __str__(self):
    return '%s - %s: %s' % (self.dataset.dataset_id, self.speaker, self.text)