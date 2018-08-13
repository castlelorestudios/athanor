# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-12 07:54
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import timezone_field.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comms', '0016_remove_channeldb_db_subscriptions'),
        ('objects', '0009_remove_objectdb_db_player'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountCharacter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('extra_character_slots', models.SmallIntegerField(default=0)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('characters', models.ManyToManyField(related_name='_accountcharacter_characters_+', to='objects.ObjectDB')),
                ('last_character', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='objects.ObjectDB')),
            ],
        ),
        migrations.CreateModel(
            name='AccountCore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banned', models.DateTimeField(null=True)),
                ('disabled', models.BooleanField(default=False)),
                ('playtime', models.DurationField(default=datetime.timedelta(0))),
                ('last_login', models.DateTimeField(null=True)),
                ('last_logout', models.DateTimeField(null=True)),
                ('shelved', models.BooleanField(default=False)),
                ('timezone', timezone_field.fields.TimeZoneField(default=b'UTC')),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AccountOnline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CharacterCharacter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('character', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='objects.ObjectDB')),
            ],
        ),
        migrations.CreateModel(
            name='CharacterCore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banned', models.DateTimeField(null=True)),
                ('disabled', models.BooleanField(default=False)),
                ('playtime', models.DurationField(default=datetime.timedelta(0))),
                ('last_login', models.DateTimeField(null=True)),
                ('last_logout', models.DateTimeField(null=True)),
                ('shelved', models.BooleanField(default=False)),
                ('dark', models.BooleanField(default=False)),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('character', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='objects.ObjectDB')),
            ],
        ),
        migrations.CreateModel(
            name='CharacterOnline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('character', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='objects.ObjectDB')),
            ],
        ),
        migrations.CreateModel(
            name='PublicChannelAccountMuzzle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('until_date', models.DateTimeField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='muzzles', to=settings.AUTH_USER_MODEL)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_muzzles', to='comms.ChannelDB')),
            ],
        ),
        migrations.CreateModel(
            name='PublicChannelMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('markup_text', models.TextField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='comms.ChannelDB')),
                ('speaker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='objects.ObjectDB')),
            ],
        ),
        migrations.AddIndex(
            model_name='publicchannelmessage',
            index=models.Index(fields=[b'channel', b'date_created'], name='athanor_pub_channel_7c9e64_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='publicchannelaccountmuzzle',
            unique_together=set([('channel', 'account')]),
        ),
    ]
