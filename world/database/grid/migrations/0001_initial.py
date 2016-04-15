# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-15 03:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('objects', '0005_auto_20150403_2339'),
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100, unique=True)),
                ('lock_storage', models.TextField(blank=True, verbose_name='locks')),
                ('setting_ic', models.BooleanField(default=True)),
                ('order', models.SmallIntegerField(default=100)),
                ('description', models.TextField(blank=True, default='This District has no Description!')),
                ('rooms', models.ManyToManyField(related_name='district', to='objects.ObjectDB')),
            ],
        ),
    ]
