# Generated by Django 3.2.9 on 2022-01-25 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0003_profiledata'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='privat',
            field=models.BooleanField(default=False),
        ),
    ]