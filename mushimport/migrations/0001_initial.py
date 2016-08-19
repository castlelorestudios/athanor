# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-18 21:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('objects', '0005_auto_20150403_2339'),
        ('groups', '0001_initial'),
        ('bbs', '0002_auto_20160818_2137'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fclist', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MushAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MushAttributeName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MushObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dbref', models.CharField(db_index=True, max_length=15)),
                ('objid', models.CharField(db_index=True, max_length=30, unique=True)),
                ('type', models.PositiveSmallIntegerField(db_index=True)),
                ('name', models.CharField(max_length=80)),
                ('created', models.DateTimeField()),
                ('flags', models.TextField(blank=True)),
                ('recreated', models.BooleanField(default=0)),
                ('account', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mush', to=settings.AUTH_USER_MODEL)),
                ('board', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mush', to='bbs.Board')),
                ('destination', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exits_to', to='mushimport.MushObject')),
                ('fclist', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mush', to='fclist.FCList')),
                ('group', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mush', to='groups.Group')),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='mushimport.MushObject')),
                ('obj', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mush', to='objects.ObjectDB')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned', to='mushimport.MushObject')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='mushimport.MushObject')),
            ],
        ),
        migrations.AddField(
            model_name='mushattribute',
            name='attr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='characters', to='mushimport.MushAttributeName'),
        ),
        migrations.AddField(
            model_name='mushattribute',
            name='dbref',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attrs', to='mushimport.MushObject'),
        ),
        migrations.AlterUniqueTogether(
            name='mushattribute',
            unique_together=set([('dbref', 'attr')]),
        ),
    ]