# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-29 10:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import the_platform.util


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_profile_points'),
        ('bets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlacedBinaryBet',
            fields=[
                ('prim_key', models.PositiveIntegerField(default=the_platform.util.pkgen, primary_key=True, serialize=False)),
                ('placed_amount', models.PositiveIntegerField()),
                ('chose_alternative', models.BooleanField()),
                ('placed_date', models.DateTimeField(auto_now_add=True)),
                ('placed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Profile')),
            ],
        ),
        migrations.RemoveField(
            model_name='binarybet',
            name='id',
        ),
        migrations.AddField(
            model_name='binarybet',
            name='prim_key',
            field=models.PositiveIntegerField(default=the_platform.util.pkgen, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='binarybet',
            name='resolved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='placedbinarybet',
            name='placed_on',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bets.BinaryBet'),
        ),
    ]
