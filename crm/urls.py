# urls.py
from django.urls import path
from .views import CRMView, ClienteDetailView, ClienteUpdateView, ClienteDeleteView

urlpatterns = [
    path('', CRMView.as_view(), name='crm_home'),
    path('clientes/<int:pk>/', ClienteDetailView.as_view(), name='cliente_detail'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente_edit'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'),
]