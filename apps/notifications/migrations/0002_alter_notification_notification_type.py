# Generated by Django 5.1.1 on 2025-01-11 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[("message", "Message"), ("interest", "Interest")],
                default="message",
                max_length=10,
            ),
        ),
    ]
