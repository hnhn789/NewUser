# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-09 09:04
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BoughtItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.IntegerField(default=0)),
                ('item_quantity', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bought_items', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BoughtRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.IntegerField(default=0)),
                ('bought_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bought_record', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ItemList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('price', models.IntegerField(default=0)),
                ('remain', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='QRcodeList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_content', models.SlugField(max_length=40, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='QRCodeRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_content', models.CharField(max_length=40)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('points_got', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qrcode_record', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QRcodeStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.SlugField(max_length=40, unique=True)),
                ('last_read', models.DateTimeField(default=datetime.datetime(2017, 3, 9, 9, 4, 12, 600125))),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qrcode_status', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
