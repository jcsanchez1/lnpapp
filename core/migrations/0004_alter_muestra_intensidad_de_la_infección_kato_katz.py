# Generated by Django 5.1.4 on 2025-01-13 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_muestra_intensidad_de_la_infección_kato_katz'),
    ]

    operations = [
        migrations.AlterField(
            model_name='muestra',
            name='Intensidad_de_la_Infección_KATO_KATZ',
            field=models.CharField(choices=[('L', 'Leve'), ('M', 'Moderada'), ('S', 'Severa'), ('N', 'No se observa')], default='L', max_length=2, null=True, verbose_name='Intensidad de la Infección KATO-KATZ'),
        ),
    ]
