# Generated by Django 2.2.14 on 2020-07-21 12:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_auto_20200721_0931'),
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(blank=True, max_length=64, null=True)),
                ('city', models.CharField(blank=True, max_length=64, null=True)),
                ('device', models.CharField(blank=True, max_length=64, null=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
    ]
