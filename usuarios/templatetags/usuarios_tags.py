# usuarios/templatetags/usuarios_tags.py
from django import template
from ..models import CompanySettings

register = template.Library()

@register.simple_tag
def get_company_settings():
    obj, created = CompanySettings.objects.get_or_create(pk=1)
    return obj