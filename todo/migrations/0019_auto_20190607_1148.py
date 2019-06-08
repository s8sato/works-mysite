# Generated by Django 2.0 on 2019-06-07 02:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0018_auto_20190607_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2019, 6, 7, 12, 48, 44, 597885), verbose_name='納期'),
        ),
        migrations.AlterField(
            model_name='task',
            name='start',
            field=models.DateTimeField(default=datetime.datetime(2019, 6, 7, 11, 48, 44, 597697), null=True, verbose_name='着手日時'),
        ),
    ]