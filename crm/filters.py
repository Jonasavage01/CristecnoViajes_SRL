# filters.py
from django.db.models import Q
from django.core.exceptions import ValidationError

class ClienteFilter:
    FILTER_PARAMS = ['q', 'fecha_creacion_desde', 'fecha_creacion_hasta', 'estado']
    
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
            query_terms = search_query.split()
            queries = []
            
            for term in query_terms:
                term_query = (
                    Q(nombre__icontains=term) |
                    Q(apellido__icontains=term) |
                    Q(email__icontains=term) |
                    Q(cedula_pasaporte__icontains=term)
                )
                queries.append(term_query)
            
            final_query = queries.pop()
            for query in queries:
                final_query &= query
                
            self.queryset = self.queryset.filter(final_query)

    def _validate_dates(self, fecha_desde, fecha_hasta):
        if fecha_desde and fecha_hasta:
            if fecha_desde > fecha_hasta:
                raise ValidationError("La fecha inicial no puede ser mayor a la final")
            return True
        return False

    def _apply_date_filter(self):
        fecha_desde = self.params.get('fecha_creacion_desde')
        fecha_hasta = self.params.get('fecha_creacion_hasta')
        if self._validate_dates(fecha_desde, fecha_hasta):
            self.queryset = self.queryset.filter(
                fecha_creacion__date__range=[fecha_desde, fecha_hasta]
            )

    def _apply_estado_filter(self):
        if estado := self.params.get('estado'):
            valid_states = [choice[0] for choice in self.queryset.model.ESTADO_CHOICES]
            if estado in valid_states:
                self.queryset = self.queryset.filter(estado__iexact=estado)

    @property
    def has_active_filters(self):
        return any(self.params.get(param) for param in self.FILTER_PARAMS)

    @property
    def filtered_count(self):
        return self.queryset.count()

    @property
    def filtering_applied(self):
        return self.filtered_count != self.original_count