# Generated by Django 3.1.4 on 2020-12-31 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='url',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='survey',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='survey',
            name='title',
            field=models.CharField(default='', max_length=100),
        ),
    ]
