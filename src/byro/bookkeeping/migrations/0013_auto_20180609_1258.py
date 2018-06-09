# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-09 12:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookkeeping', '0012_auto_20180609_1145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='realtransaction',
            name='reverses',
        ),
        migrations.RemoveField(
            model_name='realtransaction',
            name='source',
        ),
        migrations.RemoveField(
            model_name='virtualtransaction',
            name='destination_account',
        ),
        migrations.RemoveField(
            model_name='virtualtransaction',
            name='member',
        ),
        migrations.RemoveField(
            model_name='virtualtransaction',
            name='real_transaction',
        ),
        migrations.RemoveField(
            model_name='virtualtransaction',
            name='source_account',
        ),
        migrations.AlterField(
            model_name='account',
            name='account_category',
            field=models.CharField(choices=[('asset', 'Asset account'), ('liability', 'Liability account'), ('income', 'Income account'), ('expense', 'Expense account'), ('equity', 'Equity account')], max_length=9),
        ),
        migrations.AlterField(
            model_name='booking',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='bookkeeping.Account'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='member',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='members.Member'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='bookkeeping.Transaction'),
        ),
        migrations.AlterField(
            model_name='realtransactionsource',
            name='state',
            field=models.CharField(choices=[('new', 'new'), ('processing', 'processing'), ('processed', 'processed'), ('failed', 'failed')], default='new', max_length=10),
        ),
        migrations.DeleteModel(
            name='RealTransaction',
        ),
        migrations.DeleteModel(
            name='VirtualTransaction',
        ),
    ]