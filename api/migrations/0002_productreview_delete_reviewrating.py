# Generated by Django 4.2 on 2023-12-07 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('star_rating', models.IntegerField(choices=[(1, '1 star'), (2, '2 stars'), (3, '3 stars'), (4, '4 stars'), (5, '5 stars')])),
                ('product_name', models.CharField(max_length=255)),
                ('generated_review', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='ReviewRating',
        ),
    ]