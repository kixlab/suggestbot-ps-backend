# Generated by Django 3.1.2 on 2020-11-13 10:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0004_moment_possible_line'),
    ]

    operations = [
        migrations.AddField(
            model_name='moment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='moment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fas1', models.IntegerField()),
                ('fas2', models.IntegerField()),
                ('fas3', models.IntegerField()),
                ('pus1', models.IntegerField()),
                ('pus2', models.IntegerField()),
                ('pus3', models.IntegerField()),
                ('aes1', models.IntegerField()),
                ('aes2', models.IntegerField()),
                ('aes3', models.IntegerField()),
                ('rws1', models.IntegerField()),
                ('rws2', models.IntegerField()),
                ('rws3', models.IntegerField()),
                ('sanity_check', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]