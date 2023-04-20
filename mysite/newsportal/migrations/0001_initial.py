# Generated by Django 4.2 on 2023-04-12 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('antraste', models.CharField(max_length=100, verbose_name='Antraste')),
                ('kategorija', models.CharField(max_length=30, verbose_name='Kategorija')),
                ('autorius', models.CharField(max_length=50, verbose_name='Autorius')),
                ('naujiena', models.TextField(verbose_name='Jusu naujiena')),
                ('paskelbimo_data', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Reklama',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nuotrauka', models.ImageField(blank=True, null=True, upload_to='Reklamos_images/')),
                ('papildoma_info', models.TextField(verbose_name='Rusu reklamos textas')),
            ],
        ),
    ]
