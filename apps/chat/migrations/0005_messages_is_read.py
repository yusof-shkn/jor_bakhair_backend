# Generated by Django 5.1.1 on 2025-01-15 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0004_alter_interest_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="messages",
            name="is_read",
            field=models.BooleanField(default=False),
        ),
    ]
