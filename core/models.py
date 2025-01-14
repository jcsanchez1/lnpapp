from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Expediente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    dni = models.CharField(max_length=15, unique=True, verbose_name="DNI")
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    apellido = models.CharField(max_length=50, verbose_name="Apellido")
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)

    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        verbose_name="Sexo"
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.dni}"

class Region(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Región")
    numero_region = models.IntegerField(unique=True, verbose_name="Número de Región")

    def __str__(self):
        return f"Región {self.numero_region}: {self.nombre}"


class CentroAtencion(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Centro")
    direccion = models.TextField(verbose_name="Dirección")
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name='centros_atencion',
        verbose_name="Región"
    )

    def __str__(self):
        return f"{self.nombre} - {self.region.nombre}"
    
# Perfil del usuario vinculado a un Centro de Atención
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    centro_atencion = models.ForeignKey(
        CentroAtencion, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Centro de Atención"
    )

    def __str__(self):
        return f"{self.user.username} - {self.centro_atencion.nombre if self.centro_atencion else 'Sin Centro'}"


# Modelo Muestra
class Muestra(models.Model):
    CONSISTENCIA_CHOICES = [
        ('F', 'Formada'),
        ('B', 'Blanda'),
        ('D', 'Diarreica'),
    ]

    MOCO_CHOICES = [
        ('E', 'Escaso'),
        ('M', 'Moderado'),
        ('A', 'Abundante'),
        ('N', 'No se observa'),
    ]

    INTENSIDAD_CHOICES = [
        ('L', 'Leve'),
        ('M', 'Moderada'),
        ('S', 'Severa'),
        ('N', 'No se observa'),
    ]
    PRESENTE_CHOICES = [
        ('P', 'Presente'),
        ('A', 'Ausente'),
    ]
    ESTADIOS_CHOICES = [
        ('T', 'Trofozoíto'),
        ('Q', 'Quiste'),
        ('TQ','Trofozoíto y Quiste'),
        ('N', 'No se observa'),
    ]
    ESTADIOS1_CHOICES = [
        ('Q', 'Quiste'),
        ('N', 'No se observa'),
    ]
    ESTADIOS2_CHOICES = [
        ('O', 'Ooquiste'),
        ('N', 'No se observa'),
    ]
    ESTADIOS3_CHOICES = [
        ('L', 'Larva'),
        ('N', 'No se observa'),
    ]
    ESTADIOS4_CHOICES = [
        ('H','Huevos'),
        ('G', 'Gusano Adulto'),
        ('N', 'No se observa'),
    ]
    ESTADIOS5_CHOICES = [
        ('H','Huevos'),
        ('G', 'Gusano Adulto'),
        ('P', 'Proglotidos'),
        ('N', 'No se observa'),
    ]
    fecha = models.DateField(auto_now_add=True)
    Expediente = models.ForeignKey(Expediente, on_delete=models.PROTECT, related_name='muestras')
    Edad = models.IntegerField()
    consistencia = models.CharField(max_length=2, choices=CONSISTENCIA_CHOICES, verbose_name="Consistencia")
    moco = models.CharField(max_length=2, choices=MOCO_CHOICES, verbose_name="Moco")
    sangre_macroscopica = models.CharField(max_length=2,choices=PRESENTE_CHOICES, verbose_name="Sangre Macroscópica")
    Entamoeba_histolytica = models.CharField(max_length=2, choices=ESTADIOS_CHOICES, verbose_name="Entamoeba histolytica")
    Entamoeba_coli = models.CharField(max_length=2, choices=ESTADIOS_CHOICES, verbose_name="Entamoeba coli")
    Entamoeba_hartmanni = models.CharField(max_length=2, choices=ESTADIOS_CHOICES, verbose_name="Entamoeba hartmanni")
    Endolimax_nana = models.CharField(max_length=2, choices=ESTADIOS_CHOICES, verbose_name="Endolimax nana")
    Iodamoeba_bütschlii = models.CharField(max_length=2, choices=ESTADIOS_CHOICES, verbose_name="Iodamoeba bütschlii")
    Blastocystis_sp = models.CharField(max_length=2, choices=ESTADIOS2_CHOICES, verbose_name="Blastocystis sp")
    Giardia_intestinalis = models.CharField(max_length=2, choices=ESTADIOS_CHOICES, verbose_name="Giardia intestinalis")
    Pentatrichomonas_hominis = models.CharField(max_length=2, choices=ESTADIOS_CHOICES, verbose_name="Pentatrichomonas hominis")
    Chilomastix_mesnili = models.CharField(max_length=2, choices=ESTADIOS_CHOICES, verbose_name="Chilomastix mesnili")
    Balantidium_coli = models.CharField(max_length=2, choices=ESTADIOS_CHOICES, verbose_name="Balantidium coli")
    Cystoisospora_belli = models.CharField(max_length=2,choices=ESTADIOS2_CHOICES, verbose_name="Cystoisospora belli")
    Cyclospora_cayetanensis = models.CharField(max_length=2, choices=ESTADIOS2_CHOICES, verbose_name="Cyclospora cayetanensis")
    Criptosporidium_spp = models.CharField(max_length=2, choices=ESTADIOS2_CHOICES, verbose_name="Criptosporidium spp")
    Strongyloides_stercoralis = models.CharField(max_length=2, choices=ESTADIOS3_CHOICES, verbose_name="Strongyloides stercoralis")
    Ascaris_lumbricoides = models.CharField(max_length=2, choices=ESTADIOS4_CHOICES, verbose_name="Ascaris lumbricoides")
    Trichuris_trichiura = models.CharField(max_length=2, choices=ESTADIOS4_CHOICES, verbose_name="Trichuris trichiura")
    Necator_americanus = models.CharField(max_length=2, choices=ESTADIOS4_CHOICES, verbose_name="Necator americanus")
    Enterobius_vermicularis = models.CharField(max_length=2, choices=ESTADIOS4_CHOICES, verbose_name="Enterobius vermicularis")
    Taenia_spp = models.CharField(max_length=2, choices=ESTADIOS5_CHOICES, verbose_name="Taenia spp")
    Hymenolepis_diminuta = models.CharField(max_length=2, choices=ESTADIOS4_CHOICES, verbose_name="Hymenolepis diminuta")
    Rodentolepis_nana = models.CharField(max_length=2, choices=ESTADIOS4_CHOICES, verbose_name="Rodentolepis nana")
    Intensidad_de_la_Infección_KATO_KATZ = models.CharField(max_length=2, choices=INTENSIDAD_CHOICES, verbose_name="Intensidad de la Infección KATO-KATZ",default='L',null=True)
    No_se_observaron_parásitos = models.BooleanField()

    def __str__(self):
        return (
            f"Fecha: {self.fecha}, "
            f"DNI: {self.Expediente.dni}, "
            f"Nombre: {self.Expediente.nombre}, "
            f"Sexo: {self.Expediente.sexo}, "
            f"Edad: {self.Edad}, "
            f"Consistencia: {self.get_consistencia_display()}, "
            f"Moco: {self.get_moco_display()}, "
            f"Sangre Macroscópica: {self.get_sangre_macroscopica_display()}, "
            f"Entamoeba histolytica: {self.get_Entamoeba_histolytica_display()}, "
            f"Entamoeba coli: {self.get_Entamoeba_coli_display()}, "
            f"Entamoeba hartmanni: {self.get_Entamoeba_hartmanni_display()}, "
            f"Endolimax nana: {self.get_Endolimax_nana_display()}, "
            f"Iodamoeba bütschlii: {self.get_Iodamoeba_bütschlii_display()}, "
            f"Blastocystis sp: {self.get_Blastocystis_sp_display()}, "
            f"Giardia intestinalis: {self.get_Giardia_intestinalis_display()}, "
            f"Pentatrichomonas hominis: {self.get_Pentatrichomonas_hominis_display()}, "
            f"Chilomastix mesnili: {self.get_Chilomastix_mesnili_display()}, "
            f"Balantidium coli: {self.get_Balantidium_coli_display()}, "
            f"Cystoisospora belli: {self.get_Cystoisospora_belli_display()}, "
            f"Cyclospora cayetanensis: {self.get_Cyclospora_cayetanensis_display()}, "
            f"Criptosporidium spp: {self.get_Criptosporidium_spp_display()}, "
            f"Strongyloides stercoralis: {self.get_Strongyloides_stercoralis_display()}, "
            f"Ascaris lumbricoides: {self.get_Ascaris_lumbricoides_display()}, "
            f"Trichuris trichiura: {self.get_Trichuris_trichiura_display()}, "
            f"Necator americanus: {self.get_Necator_americanus_display()}, "
            f"Enterobius vermicularis: {self.get_Enterobius_vermicularis_display()}, "
            f"Taenia spp: {self.get_Taenia_spp_display()}, "
            f"Hymenolepis diminuta: {self.get_Hymenolepis_diminuta_display()}, "
            f"Rodentolepis nana: {self.get_Rodentolepis_nana_display()}, "
            f"Intensidad de la Infección: {self.get_Intensidad_de_la_Infección_KATO_KATZ_display()}, "
            f"No se observaron parásitos: {'Sí' if self.No_se_observaron_parásitos else 'No'}"
        )


