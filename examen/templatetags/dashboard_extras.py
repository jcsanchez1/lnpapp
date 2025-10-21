from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un item de un diccionario por su key"""
    if dictionary and key:
        return dictionary.get(key, 0)
    return 0

@register.filter
def get_count(parasito, matriz):
    """Calcula el total de un parásito en todas las regiones"""
    total = 0
    for fila in matriz:
        total += fila['parasitos'].get(parasito, 0)
    return total

@register.filter
def sum(value):
    """Suma los valores de un iterable"""
    if value:
        try:
            return sum(value)
        except:
            return 0
    return 0