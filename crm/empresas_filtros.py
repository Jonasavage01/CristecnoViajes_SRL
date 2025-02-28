# crm/filters/empresas_filtros.py
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Empresa
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from .models import Empresa


class EmpresaFilter:
    FILTER_PARAMS = ['q', 'fecha_registro_desde', 'fecha_registro_hasta', 'estado']
    
    def __init__(self, params, queryset):
        self.params = params
        self.queryset = queryset
        self.original_count = queryset.count()

    def apply_filters(self):
        self._apply_search_filter()
        self._apply_date_filter()
        self._apply_estado_filter()
        return self.queryset

    def _apply_search_filter(self):
        if search_query := self.params.get('q'):
            exact_email_match = Q(direccion_electronica__iexact=search_query)
            partial_matches = Q()
            terms = search_query.split()
            
            # Búsqueda exacta de email
            if '@' in search_query and len(terms) == 1:
                self.queryset = self.queryset.filter(exact_email_match)
                return
            
            # Búsqueda por otros campos
            for term in terms:
                partial_matches &= (
                    Q(nombre_comercial__icontains=term) |
                    Q(rnc__icontains=term) |
                    Q(razon_social__icontains=term) |
                    Q(representante__icontains=term)
                )
            
            self.queryset = self.queryset.filter(partial_matches)

    def _validate_dates(self, fecha_desde, fecha_hasta):
        try:
            fecha_desde = parse_date(fecha_desde) if fecha_desde else None
            fecha_hasta = parse_date(fecha_hasta) if fecha_hasta else None
            
            if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
                raise ValidationError("La fecha inicial no puede ser mayor a la final")
                
            return True
        except (ValueError, TypeError):
            raise ValidationError("Formato de fecha inválido. Use YYYY-MM-DD")

    def _apply_date_filter(self):
        fecha_desde = self.params.get('fecha_registro_desde')
        fecha_hasta = self.params.get('fecha_registro_hasta')
        
        if fecha_desde or fecha_hasta:
            self._validate_dates(fecha_desde, fecha_hasta)
            
            filter_args = {}
            if fecha_desde:
                filter_args['fecha_registro__date__gte'] = fecha_desde
            if fecha_hasta:
                filter_args['fecha_registro__date__lte'] = fecha_hasta
                
            self.queryset = self.queryset.filter(**filter_args)

    @property
    def has_active_filters(self):
        return any(self.params.get(param) for param in self.FILTER_PARAMS)

    @property
    def filtered_count(self):
        return self.queryset.count()

    @property
    def filtering_applied(self):
        return self.filtered_count != self.original_count
    def _apply_estado_filter(self):
        if estado := self.params.get('estado'):
            self.queryset = self.queryset.filter(estado__iexact=estado)