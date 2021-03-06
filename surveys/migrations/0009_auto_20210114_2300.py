# Generated by Django 3.1.4 on 2021-01-14 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0008_commentary'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentary',
            name='rootComment',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='root', to='surveys.commentary'),
        ),
        migrations.AlterField(
            model_name='commentary',
            name='parentComment',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='surveys.commentary'),
        ),
    ]
