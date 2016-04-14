# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-14 07:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='radioslot',
            name='color',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='radioslot',
            unique_together=set([('key', 'character'), ('codename', 'frequency')]),
        ),
    ]