# Generated by Django 5.1.7 on 2025-03-12 09:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('svet_site', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lamp',
            name='subsection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='svet_site.subsection', verbose_name='Подраздел'),
        ),
        migrations.AlterField(
            model_name='lamp',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='svet_site.finalsection', verbose_name='Раздел'),
        ),
    ]
