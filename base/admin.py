from django.contrib import admin
from .models import Moment, Survey, Log
# Register your models here.
admin.site.register(Moment)
admin.site.register(Survey)
admin.site.register(Log)