# Generated by Django 5.0.7 on 2024-07-25 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('telefono', models.CharField(max_length=50)),
                ('correo_electronico', models.EmailField(max_length=50, unique=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]