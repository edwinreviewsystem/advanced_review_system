# Generated by Django 4.2 on 2023-12-07 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_productreview_delete_reviewrating'),
    ]

    operations = [
        migrations.AddField(
            model_name='productreview',
            name='user_word',
            field=models.CharField(default=None, max_length=200),
        ),
    ]
