# Generated by Django 3.1.6 on 2021-02-09 21:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0002_auto_20210203_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='todoitem',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='auth.user'),
            preserve_default=False,
        ),
    ]
