# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-10 14:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookkeeping', '0013_auto_20180609_1258'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='text',
            new_name='memo',
        ),
        migrations.AddField(
            model_name='booking',
            name='memo',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='memo',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
