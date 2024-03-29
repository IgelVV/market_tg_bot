# Generated by Django 4.2.5 on 2023-09-07 11:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('slug', models.SlugField()),
                ('api_key', models.CharField(max_length=1024)),
                ('client_id', models.CharField(max_length=1024)),
                ('vendor_name', models.CharField(max_length=1024)),
                ('is_active', models.BooleanField(default=True)),
                ('stop_updated_price', models.BooleanField(default=False)),
                ('individual_updating_time', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'shop',
                'verbose_name_plural': 'shops',
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('ozon_id', models.CharField(max_length=1024)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.shop')),
            ],
            options={
                'verbose_name': 'storage',
                'verbose_name_plural': 'storages',
            },
        ),
    ]
