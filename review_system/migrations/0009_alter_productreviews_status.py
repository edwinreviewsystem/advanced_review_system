# Generated by Django 5.0 on 2024-05-03 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review_system', '0008_remove_productreviews_auto_approve_reviews'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productreviews',
            name='status',
            field=models.CharField(choices=[('approve', 'Approve'), ('disapprove', 'Disapprove')], default='pending', max_length=20),
        ),
    ]