# Generated by Django 2.2.12 on 2020-10-12 05:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('runners', '0010_auto_20180903_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runtime',
            name='url',
            field=models.URLField(blank=True),
        ),
        migrations.CreateModel(
            name='RuntimeComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=512)),
                ('url', models.URLField()),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('runtime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='runners.Runtime')),
            ],
            options={
                'ordering': ('filename',),
            },
        ),
    ]
