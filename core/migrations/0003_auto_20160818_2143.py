# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-18 21:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20160818_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charactersetting',
            name='player',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='char_settings', to=settings.AUTH_USER_MODEL),
        ),
    ]