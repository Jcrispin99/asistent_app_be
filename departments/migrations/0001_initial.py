# Generated by Django 5.2.1 on 2025-06-04 23:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre del departamento')),
                ('codigo', models.CharField(max_length=10, verbose_name='Código del departamento')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción del departamento')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Fecha de edición')),
                ('dep_padre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='departments.department', verbose_name='Departamento padre')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company', verbose_name='Empresa')),
            ],
            options={
                'verbose_name': 'Departamento',
                'verbose_name_plural': 'Departamentos',
                'ordering': ['empresa', 'nombre'],
                'unique_together': {('empresa', 'codigo')},
            },
        ),
    ]
