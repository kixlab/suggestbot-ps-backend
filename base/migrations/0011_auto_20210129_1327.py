# Generated by Django 3.1.2 on 2021-01-29 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_survey_free_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='aes1',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='aes2',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='aes3',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='fas1',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='fas2',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='fas3',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
