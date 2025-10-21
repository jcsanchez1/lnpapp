from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('examen', '0007_sync_expediente_fields'),
    ]

    operations = [
        # Agregar campos a Region
        migrations.AddField(
            model_name='region',
            name='es_metropolitana',
            field=models.BooleanField(
                default=False,
                help_text='Regiones 19 y 20 son metropolitanas (Tegucigalpa y San Pedro Sula)',
                verbose_name='¿Es Región Metropolitana?'
            ),
        ),
        migrations.AddField(
            model_name='region',
            name='departamento',
            field=models.ForeignKey(
                blank=True,
                help_text='Solo para regiones departamentales (1-18). Regiones metropolitanas no tienen.',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='regiones',
                to='examen.departamento',
                verbose_name='Departamento'
            ),
        ),
    ]