# Generated by Django 5.0.7 on 2024-08-19 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='hora_fin_reserva',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reserva',
            name='tiempo_reserva',
            field=models.IntegerField(default=60),
        ),
    ]