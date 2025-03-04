from django.urls import path

# Imports de vistas
from .views import (
    ClienteDetailView,
    ClienteUpdateView,
    DocumentUploadView,
    NotesUpdateView,
    NoteCreateView,
    DocumentDeleteView,
    ClientePDFView,
    CRMView, ClienteDeleteView,
)
from .empresas import EmpresasView, EmpresaUpdateView,EmpresaDetailView, NotaEmpresaCreateView,DocumentoEmpresaUploadView,DeleteDocumentoEmpresaView,DeleteNotaEmpresaView, EmpresaPDFView, EmpresaDeleteView

# Definición de rutas
urlpatterns = [
    # Página principal del CRM
    path('', CRMView.as_view(), name='crm_home'),
    
     # Empresas
    path('empresas/', EmpresasView.as_view(), name='empresas'),
    path('empresas/<int:pk>/editar/', EmpresaUpdateView.as_view(), name='empresa_edit'),
    path('empresas/<int:pk>/', EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresas/<int:pk>/add_note/', NotaEmpresaCreateView.as_view(), name='add_note_empresa'),
    path('empresas/<int:pk>/subir-documento/', DocumentoEmpresaUploadView.as_view(), name='upload_documento_empresa'),
     path(
        'crm/empresas/<int:pk>/eliminar-documento/<int:doc_pk>/',
        DeleteDocumentoEmpresaView.as_view(),
        name='delete_documento_empresa'
    ),
    path('empresas/<int:pk>/eliminar-nota/<int:nota_pk>/', DeleteNotaEmpresaView.as_view(), name='delete_nota_empresa'),
     path('empresa/<int:pk>/pdf/', EmpresaPDFView.as_view(), name='empresa_pdf'),
    path('empresas/<int:pk>/eliminar/', EmpresaDeleteView.as_view(), name='empresa_delete'),

    # Gestión de clientes
    path('clientes/<int:pk>/edit/', ClienteUpdateView.as_view(), name='cliente_edit'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('clientes/<int:pk>/add_note/', NoteCreateView.as_view(), name='add_note'),

    # Gestión de documentos
    path('clientes/<int:pk>/subir-documento/', DocumentUploadView.as_view(), name='upload_document'),
    path('documentos/<int:pk>/eliminar/', DocumentDeleteView.as_view(), name='delete_document'),
    path('clientes/<int:pk>/pdf/', ClientePDFView.as_view(), name='cliente_pdf'),

    # Detalle del cliente (debe estar al final para evitar conflictos con otras rutas)
    path('clientes/<int:pk>/', ClienteDetailView.as_view(), name='cliente_detail'),
]
