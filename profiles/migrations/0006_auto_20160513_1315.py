# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-13 13:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_profile_accepted_agbs'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='accepted_agbs',
            new_name='accepted_agb',
        ),
    ]
