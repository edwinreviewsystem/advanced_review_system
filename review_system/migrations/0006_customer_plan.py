# Generated by Django 5.0 on 2025-05-15 11:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review_system', '0005_remove_customer_plan_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='plan',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='review_system.plans'),
        ),
    ]
