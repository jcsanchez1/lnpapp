# examen/management/commands/cargar_departamentos_municipios.py

from django.core.management.base import BaseCommand
from examen.models import Departamento, Municipio

class Command(BaseCommand):
    help = 'Carga los 18 departamentos y 298 municipios de Honduras'

    def handle(self, *args, **kwargs):
        self.stdout.write('🗺️  Cargando Departamentos y Municipios de Honduras...\n')
        
        # DATOS COMPLETOS
        datos = {
            "01": {
                "nombre": "Atlántida",
                "extension": 4251,
                "municipios": [
                    ("0101", "La Ceiba", True),
                    ("0102", "El Porvenir", False),
                    ("0103", "Esparta", False),
                    ("0104", "Jutiapa", False),
                    ("0105", "La Masica", False),
                    ("0106", "San Francisco", False),
                    ("0107", "Tela", False),
                    ("0108", "Arizona", False),
                ]
            },
            "02": {
                "nombre": "Colón",
                "extension": 8875,
                "municipios": [
                    ("0201", "Trujillo", True),
                    ("0202", "Balfate", False),
                    ("0203", "Iriona", False),
                    ("0204", "Limón", False),
                    ("0205", "Sabá", False),
                    ("0206", "Santa Fe", False),
                    ("0207", "Santa Rosa de Aguán", False),
                    ("0208", "Sonaguera", False),
                    ("0209", "Tocoa", False),
                    ("0210", "Bonito Oriental", False),
                ]
            },
            "03": {
                "nombre": "Comayagua",
                "extension": 5196,
                "municipios": [
                    ("0301", "Comayagua", True),
                    ("0302", "Ajuterique", False),
                    ("0303", "El Rosario", False),
                    ("0304", "Esquías", False),
                    ("0305", "Humuya", False),
                    ("0306", "La Libertad", False),
                    ("0307", "Lamaní", False),
                    ("0308", "La Trinidad", False),
                    ("0309", "Lejamaní", False),
                    ("0310", "Meámbar", False),
                    ("0311", "Minas de Oro", False),
                    ("0312", "Ojo de Agua", False),
                    ("0313", "San Jerónimo", False),
                    ("0314", "San José de Comayagua", False),
                    ("0315", "San José del Potrero", False),
                    ("0316", "San Luis", False),
                    ("0317", "San Sebastián", False),
                    ("0318", "Siguatepeque", False),
                    ("0319", "Villa de San Antonio", False),
                    ("0320", "Lajas", False),
                    ("0321", "Taulabe", False),
                ]
            },
            "04": {
                "nombre": "Copán",
                "extension": 3242,
                "municipios": [
                    ("0401", "Santa Rosa de Copán", True),
                    ("0402", "Cabañas", False),
                    ("0403", "Concepción", False),
                    ("0404", "Copán Ruinas", False),
                    ("0405", "Corquín", False),
                    ("0406", "Cucuyagua", False),
                    ("0407", "Dolores", False),
                    ("0408", "Dulce Nombre", False),
                    ("0409", "El Paraíso", False),
                    ("0410", "Florida", False),
                    ("0411", "La Jigua", False),
                    ("0412", "La Unión", False),
                    ("0413", "Nueva Arcadia", False),
                    ("0414", "San Agustín", False),
                    ("0415", "San Antonio", False),
                    ("0416", "San Jerónimo", False),
                    ("0417", "San José", False),
                    ("0418", "San Juan de Opoa", False),
                    ("0419", "San Nicolás", False),
                    ("0420", "San Pedro", False),
                    ("0421", "Santa Rita", False),
                    ("0422", "Trinidad de Copán", False),
                    ("0423", "Veracruz", False),
                ]
            },
            "05": {
                "nombre": "Cortés",
                "extension": 3954,
                "municipios": [
                    ("0501", "San Pedro Sula", True),
                    ("0502", "Choloma", False),
                    ("0503", "Omoa", False),
                    ("0504", "Pimienta", False),
                    ("0505", "Potrerillos", False),
                    ("0506", "Puerto Cortés", False),
                    ("0507", "San Antonio de Cortés", False),
                    ("0508", "San Francisco de Yojoa", False),
                    ("0509", "San Manuel", False),
                    ("0510", "Santa Cruz de Yojoa", False),
                    ("0511", "Villanueva", False),
                    ("0512", "La Lima", False),
                ]
            },
            "06": {
                "nombre": "Choluteca",
                "extension": 4360,
                "municipios": [
                    ("0601", "Choluteca", True),
                    ("0602", "Apacilagua", False),
                    ("0603", "Concepción de María", False),
                    ("0604", "Duyure", False),
                    ("0605", "El Corpus", False),
                    ("0606", "El Triunfo", False),
                    ("0607", "Marcovia", False),
                    ("0608", "Morolica", False),
                    ("0609", "Namasigüe", False),
                    ("0610", "Orocuina", False),
                    ("0611", "Pespire", False),
                    ("0612", "San Antonio de Flores", False),
                    ("0613", "San Isidro", False),
                    ("0614", "San José", False),
                    ("0615", "San Marcos de Colón", False),
                    ("0616", "Santa Ana de Yusguare", False),
                ]
            },
            "07": {
                "nombre": "El Paraíso",
                "extension": 7218,
                "municipios": [
                    ("0701", "Yuscarán", True),
                    ("0702", "Alauca", False),
                    ("0703", "Danlí", False),
                    ("0704", "El Paraíso", False),
                    ("0705", "Güinope", False),
                    ("0706", "Jacaleapa", False),
                    ("0707", "Liure", False),
                    ("0708", "Morocelí", False),
                    ("0709", "Oropolí", False),
                    ("0710", "Potrerillos", False),
                    ("0711", "San Antonio de Flores", False),
                    ("0712", "San Lucas", False),
                    ("0713", "San Matías", False),
                    ("0714", "Soledad", False),
                    ("0715", "Teupasenti", False),
                    ("0716", "Texiguat", False),
                    ("0717", "Vado Ancho", False),
                    ("0718", "Yauyupe", False),
                    ("0719", "Trojes", False),
                ]
            },
            "08": {
                "nombre": "Francisco Morazán",
                "extension": 8619,
                "municipios": [
                    ("0801", "Tegucigalpa D.C.", True),
                    ("0802", "Alubarén", False),
                    ("0803", "Cedros", False),
                    ("0804", "Curarén", False),
                    ("0805", "El Porvenir", False),
                    ("0806", "Guaimaca", False),
                    ("0807", "La Libertad", False),
                    ("0808", "La Venta", False),
                    ("0809", "Lepaterique", False),
                    ("0810", "Maraita", False),
                    ("0811", "Marale", False),
                    ("0812", "Nueva Armenia", False),
                    ("0813", "Ojojona", False),
                    ("0814", "Orica", False),
                    ("0815", "Reitoca", False),
                    ("0816", "Sabanagrande", False),
                    ("0817", "San Antonio de Oriente", False),
                    ("0818", "San Buenaventura", False),
                    ("0819", "San Ignacio", False),
                    ("0820", "San Juan de Flores", False),
                    ("0821", "San Miguelito", False),
                    ("0822", "Santa Ana", False),
                    ("0823", "Santa Lucía", False),
                    ("0824", "Talanga", False),
                    ("0825", "Tatumbla", False),
                    ("0826", "Valle de Ángeles", False),
                    ("0827", "Villa de San Francisco", False),
                    ("0828", "Vallecillo", False),
                ]
            },
            "09": {
                "nombre": "Gracias a Dios",
                "extension": 16630,
                "municipios": [
                    ("0901", "Puerto Lempira", True),
                    ("0902", "Brus Laguna", False),
                    ("0903", "Ahuas", False),
                    ("0904", "Juan Francisco Bulnes", False),
                    ("0905", "Villeda Morales", False),
                    ("0906", "Wampusirpi", False),
                ]
            },
            "10": {
                "nombre": "Intibucá",
                "extension": 3072,
                "municipios": [
                    ("1001", "La Esperanza", True),
                    ("1002", "Camasca", False),
                    ("1003", "Colomoncagua", False),
                    ("1004", "Concepción", False),
                    ("1005", "Dolores", False),
                    ("1006", "Intibucá", False),
                    ("1007", "Jesús de Otoro", False),
                    ("1008", "Magdalena", False),
                    ("1009", "Masaguara", False),
                    ("1010", "San Antonio", False),
                    ("1011", "San Isidro", False),
                    ("1012", "San Juan de Flores", False),
                    ("1013", "San Marcos de La Sierra", False),
                    ("1014", "San Miguel Guancapla", False),
                    ("1015", "Santa Lucía", False),
                    ("1016", "Yamaranguila", False),
                    ("1017", "San Francisco Opalaca", False),
                ]
            },
            "11": {
                "nombre": "Islas de la Bahía",
                "extension": 260,
                "municipios": [
                    ("1101", "Roatán", True),
                    ("1102", "Guanaja", False),
                    ("1103", "José Santos Guardiola", False),
                    ("1104", "Utila", False),
                ]
            },
            "12": {
                "nombre": "La Paz",
                "extension": 2331,
                "municipios": [
                    ("1201", "La Paz", True),
                    ("1202", "Aguanqueterique", False),
                    ("1203", "Cabañas", False),
                    ("1204", "Cane", False),
                    ("1205", "Chinacla", False),
                    ("1206", "Guajiquiro", False),
                    ("1207", "Lauterique", False),
                    ("1208", "Marcala", False),
                    ("1209", "Mercedes de Oriente", False),
                    ("1210", "Opatoro", False),
                    ("1211", "San Antonio del Norte", False),
                    ("1212", "San José", False),
                    ("1213", "San Juan", False),
                    ("1214", "San Pedro de Tutule", False),
                    ("1215", "Santa Ana", False),
                    ("1216", "Santa Elena", False),
                    ("1217", "Santa María", False),
                    ("1218", "Santiago Puringla", False),
                    ("1219", "Yarula", False),
                ]
            },
            "13": {
                "nombre": "Lempira",
                "extension": 4228,
                "municipios": [
                    ("1301", "Gracias", True),
                    ("1302", "Belén", False),
                    ("1303", "Candelaria", False),
                    ("1304", "Cololaca", False),
                    ("1305", "Erandique", False),
                    ("1306", "Gualcinse", False),
                    ("1307", "Guarita", False),
                    ("1308", "La Campa", False),
                    ("1309", "La Iguala", False),
                    ("1310", "Las Flores", False),
                    ("1311", "La Unión", False),
                    ("1312", "La Virtud", False),
                    ("1313", "Lepaera", False),
                    ("1314", "Mapulaca", False),
                    ("1315", "Piraera", False),
                    ("1316", "San Andrés", False),
                    ("1317", "San Francisco", False),
                    ("1318", "San Juan Guarita", False),
                    ("1319", "San Manuel Colohete", False),
                    ("1320", "San Rafael", False),
                    ("1321", "San Sebastián", False),
                    ("1322", "Santa Cruz", False),
                    ("1323", "Talgua", False),
                    ("1324", "Tambla", False),
                    ("1325", "Tomalá", False),
                    ("1326", "Valladolid", False),
                    ("1327", "Virginia", False),
                    ("1328", "San Marcos de Caiquín", False),
                ]
            },
            "14": {
                "nombre": "Ocotepeque",
                "extension": 1680,
                "municipios": [
                    ("1401", "Nueva Ocotepeque", True),
                    ("1402", "Belén Gualcho", False),
                    ("1403", "Concepción", False),
                    ("1404", "Dolores Merendón", False),
                    ("1405", "Fraternidad", False),
                    ("1406", "La Encarnación", False),
                    ("1407", "La Labor", False),
                    ("1408", "Lucerna", False),
                    ("1409", "Mercedes", False),
                    ("1410", "San Fernando", False),
                    ("1411", "San Francisco del Valle", False),
                    ("1412", "San Jorge", False),
                    ("1413", "San Marcos", False),
                    ("1414", "Santa Fé", False),
                    ("1415", "Sensenti", False),
                    ("1416", "Sinuapa", False),
                ]
            },
            "15": {
                "nombre": "Olancho",
                "extension": 23905,
                "municipios": [
                    ("1501", "Juticalpa", True),
                    ("1502", "Campamento", False),
                    ("1503", "Catacamas", False),
                    ("1504", "Concordia", False),
                    ("1505", "Dulce Nombre de Culmí", False),
                    ("1506", "El Rosario", False),
                    ("1507", "Esquipulas del Norte", False),
                    ("1508", "Gualaco", False),
                    ("1509", "Guarizama", False),
                    ("1510", "Guata", False),
                    ("1511", "Guayape", False),
                    ("1512", "Jano", False),
                    ("1513", "La Unión", False),
                    ("1514", "Mangulile", False),
                    ("1515", "Manto", False),
                    ("1516", "Salamá", False),
                    ("1517", "San Esteban", False),
                    ("1518", "San Francisco de Becerra", False),
                    ("1519", "San Francisco de La Paz", False),
                    ("1520", "Santa María del Real", False),
                    ("1521", "Silca", False),
                    ("1522", "Yocón", False),
                    ("1523", "Patuca", False),
                ]
            },
            "16": {
                "nombre": "Santa Bárbara",
                "extension": 5321,
                "municipios": [
                    ("1601", "Santa Bárbara", True),
                    ("1602", "Arada", False),
                    ("1603", "Atima", False),
                    ("1604", "Azacualpa", False),
                    ("1605", "Ceguaca", False),
                    ("1606", "Colinas", False),
                    ("1607", "Concepción del Norte", False),
                    ("1608", "Concepción del Sur", False),
                    ("1609", "Chinda", False),
                    ("1610", "El Níspero", False),
                    ("1611", "Gualala", False),
                    ("1612", "Ilama", False),
                    ("1613", "Macuelizo", False),
                    ("1614", "Naranjito", False),
                    ("1615", "Nueva Celilac", False),
                    ("1616", "Petoa", False),
                    ("1617", "Protección", False),
                    ("1618", "Quimistán", False),
                    ("1619", "San Francisco de Ojuera", False),
                    ("1620", "San Luis", False),
                    ("1621", "San Marcos", False),
                    ("1622", "San Nicolás", False),
                    ("1623", "San Pedro Zacapa", False),
                    ("1624", "Santa Rita", False),
                    ("1625", "San Vicente Centenario", False),
                    ("1626", "Trinidad", False),
                    ("1627", "Las Vegas", False),
                    ("1628", "Nueva Frontera", False),
                ]
            },
            "17": {
                "nombre": "Valle",
                "extension": 1665,
                "municipios": [
                    ("1701", "Nacaome", True),
                    ("1702", "Alianza", False),
                    ("1703", "Amapala", False),
                    ("1704", "Aramecina", False),
                    ("1705", "Caridad", False),
                    ("1706", "Goascorán", False),
                    ("1707", "Langue", False),
                    ("1708", "San Francisco de Coray", False),
                    ("1709", "San Lorenzo", False),
                ]
            },
            "18": {
                "nombre": "Yoro",
                "extension": 7781,
                "municipios": [
                    ("1801", "Yoro", True),
                    ("1802", "Arenal", False),
                    ("1803", "El Negrito", False),
                    ("1804", "El Progreso", False),
                    ("1805", "Jocón", False),
                    ("1806", "Morazán", False),
                    ("1807", "Olanchito", False),
                    ("1808", "Santa Rita", False),
                    ("1809", "Sulaco", False),
                    ("1810", "Victoria", False),
                    ("1811", "Yorito", False),
                ]
            },
        }

        total_departamentos = 0
        total_municipios = 0

        for codigo, info in datos.items():
            # Crear o actualizar departamento
            departamento, created = Departamento.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nombre': info['nombre'],
                    'extension_territorial': info['extension']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Departamento creado: {departamento}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Departamento actualizado: {departamento}')
                )
            
            total_departamentos += 1

            # Crear municipios
            for codigo_mun, nombre_mun, es_cabecera in info['municipios']:
                municipio, created = Municipio.objects.update_or_create(
                    codigo=codigo_mun,
                    defaults={
                        'nombre': nombre_mun,
                        'departamento': departamento,
                        'es_cabecera': es_cabecera
                    }
                )
                
                if created:
                    total_municipios += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 ¡Proceso completado!\n'
                f'   📍 {total_departamentos} departamentos cargados\n'
                f'   🏘️  {total_municipios} municipios creados\n'
            )
        )