# Generated by Django 4.2.13 on 2024-05-15 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='group_avatar/'),
        ),
    ]
