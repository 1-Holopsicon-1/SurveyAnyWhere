# Generated by Django 3.1.4 on 2021-01-09 21:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20210109_0012'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproperties',
            name='access_limited',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='userproperties',
            name='banned',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
