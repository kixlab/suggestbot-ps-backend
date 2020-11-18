from django.core.management.base import BaseCommand, CommandError
from data.models import Dataset, Line
import json

class Command(BaseCommand):
  help = 'Load lines into database'

  def add_arguments(self, parser):
    parser.add_argument('filename', nargs = 1, type = str)
    parser.add_argument('dataset', nargs = 1, type = str)
  def handle(self, *args, **options):
    filename = options['filename'][0]
    dataset_id = options['dataset'][0]
    with open(filename, 'r', encoding='utf-8') as f:

      lines = json.load(f)
      dataset = Dataset(dataset_id = dataset_id)
      dataset.save()

      for l in lines:
        new_line = Line(dataset = dataset, speaker = l['speaker'], text = l['text'], starttime = l['starttime'], endtime = l['endtime'])
        new_line.save()        

      # art = json.load(f)
      # new_article = Article(title = art['title'], url = art['url'], short_name = art['short_name'])
      # new_article.save()

      # for a in art['agendas']:
      #   new_agenda = Agenda(text = a, article = new_article)
      #   new_agenda.save()
