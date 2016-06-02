# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-02 18:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ledger', '__first__'),
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForbiddenUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('has_account', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('verified', models.BooleanField(default=False)),
                ('accepted_general_terms_and_conditions', models.BooleanField(default=False)),
                ('accepted_privacy_policy', models.BooleanField(default=False)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ledger.Account')),
            ],
        ),
        migrations.AddField(
            model_name='forbiddenuser',
            name='account',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.Profile'),
        ),
    ]
