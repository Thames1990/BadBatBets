# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-10 09:46
from __future__ import unicode_literals

import bets.util
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bet',
            fields=[
                ('prim_key', models.PositiveIntegerField(default=bets.util.pkgen, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('published_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='PlacedBet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placed', models.PositiveIntegerField()),
                ('chosen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bets.Choice')),
                ('placed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='ChoiceBet',
            fields=[
                ('bet_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bets.Bet')),
            ],
            bases=('bets.bet',),
        ),
        migrations.AddField(
            model_name='placedbet',
            name='placed_on',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bets.Bet'),
        ),
        migrations.AddField(
            model_name='choice',
            name='belongs_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bets.Bet'),
        ),
        migrations.AddField(
            model_name='bet',
            name='forbidden_users',
            field=models.ManyToManyField(to='profiles.ForbiddenUser'),
        ),
        migrations.AddField(
            model_name='bet',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='choicebet',
            name='choices',
            field=models.ManyToManyField(to='bets.Choice'),
        ),
    ]
