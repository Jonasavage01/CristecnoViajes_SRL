from django.urls import path

# Imports de vistas
from .cliente_page import (
    ClienteDetailView,
    ClienteUpdateView,
    DocumentUploadView,
    NotesUpdateView,
    NoteCreateView,
    DocumentDeleteView
)
from .views import CRMView, ClienteDeleteView

# Definición de rutas
urlpatterns = [
    # Página principal del CRM
    path('', CRMView.as_view(), name='crm_home'),

    # Gestión de clientes
    path('clientes/<int:pk>/edit/', ClienteUpdateView.as_view(), name='cliente_edit'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('clientes/<int:pk>/add_note/', NoteCreateView.as_view(), name='add_note'),

    # Gestión de documentos
    path('clientes/<int:pk>/subir-documento/', DocumentUploadView.as_view(), name='upload_document'),
    path('documentos/<int:pk>/eliminar/', DocumentDeleteView.as_view(), name='delete_document'),

    # Detalle del cliente (debe estar al final para evitar conflictos con otras rutas)
    path('clientes/<int:pk>/', ClienteDetailView.as_view(), name='cliente_detail'),
]
