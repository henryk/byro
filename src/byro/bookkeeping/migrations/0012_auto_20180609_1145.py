# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-09 11:45
from __future__ import unicode_literals

import byro.common.models.auditable
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookkeeping', '0011_auto_20180303_1745'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_type', models.CharField(choices=[('debit', 'Soll'), ('credit', 'Haben')], max_length=6)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('importer', models.CharField(max_length=500, null=True)),
            ],
            bases=(byro.common.models.auditable.Auditable, models.Model),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_datetime', models.DateTimeField(null=True)),
                ('value_datetime', models.DateTimeField(null=True)),
                ('text', models.CharField(max_length=1000)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('reverses', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='bookkeeping.Transaction')),
            ],
            bases=(byro.common.models.auditable.Auditable, models.Model),
        ),
        migrations.AlterField(
            model_name='account',
            name='account_category',
            field=models.CharField(choices=[('member_donation', 'Donation account'), ('member_fees', 'Membership fee account'), ('asset', 'Asset account'), ('liability', 'Liability account'), ('income', 'Income account'), ('expense', 'Expense account'), ('equity', 'Equity account')], max_length=15),
        ),
        migrations.AlterField(
            model_name='realtransactionsource',
            name='state',
            field=models.CharField(choices=[('new', 'new'), ('failed', 'failed'), ('processing', 'processing'), ('processed', 'processed')], default='new', max_length=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='bookkeeping.Account'),
        ),
        migrations.AddField(
            model_name='booking',
            name='member',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='members.Member'),
        ),
        migrations.AddField(
            model_name='booking',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='bookkeeping.Transaction'),
        ),
    ]