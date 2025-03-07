from django.urls import path

# Importación de vistas
from .views import (
    ClienteDetailView,
    ClienteUpdateView,
    DocumentUploadView,
    NotesUpdateView,
    DeleteNoteView,
    NoteCreateView,
    DocumentDeleteView,
    ClientePDFView,
    CRMView,
    ClienteDeleteView,
    ExportClientesView
)
from .empresas import (
    EmpresasView,
    EmpresaUpdateView,
    EmpresaDetailView,
    NotaEmpresaCreateView,
    DocumentoEmpresaUploadView,
    DeleteDocumentoEmpresaView,
    DeleteNotaEmpresaView,
    EmpresaPDFView,
    EmpresaDeleteView,
    ExportEmpresasView
)

urlpatterns = [
    # ==============================
    # Página principal del CRM
    # ==============================
    path('', CRMView.as_view(), name='crm_home'),

    # ==============================
    # URLs de Gestión de Empresas
    # ==============================
    # Listado principal de empresas
    # Gestión de documentos de cliente
    path('clientes/<int:pk>/subir-documento/', DocumentUploadView.as_view(), name='upload_document'),
    path(
        'clientes/<int:cliente_pk>/eliminar-documento/<int:doc_pk>/',
        DocumentDeleteView.as_view(),
        name='delete_document'
    ),

    
    path('empresas/', EmpresasView.as_view(), name='empresas'),
    
    # Detalle de empresa (debe ir antes que las rutas con parámetros)
    path('empresas/<int:pk>/', EmpresaDetailView.as_view(), name='empresa_detail'),
    
    # Edición de empresa
    path('empresas/<int:pk>/editar/', EmpresaUpdateView.as_view(), name='empresa_edit'),
    
    # Eliminación de empresa
    path('empresas/<int:pk>/eliminar/', EmpresaDeleteView.as_view(), name='empresa_delete'),
    
    # Gestión de notas de empresa
    path('empresas/<int:pk>/add_note/', NotaEmpresaCreateView.as_view(), name='add_note_empresa'),
    path('empresas/<int:pk>/eliminar-nota/<int:nota_pk>/', DeleteNotaEmpresaView.as_view(), name='delete_nota_empresa'),
    
    # Gestión de documentos de empresa
    path('empresas/<int:pk>/subir-documento/', DocumentoEmpresaUploadView.as_view(), name='upload_documento_empresa'),
    path('empresas/<int:pk>/eliminar-documento/<int:doc_pk>/', DeleteDocumentoEmpresaView.as_view(), name='delete_documento_empresa'),
    
    # Exportación de empresas
    path('empresas/exportar/<str:formato>/', ExportEmpresasView.as_view(), name='exportar_empresas'),
    
    # Generación de PDF de empresa
    path('empresas/<int:pk>/pdf/', EmpresaPDFView.as_view(), name='empresa_pdf'),

    # ==============================
    # URLs de Gestión de Clientes
    # ==============================
    # Detalle de cliente (debe ir al final para evitar conflictos)
    path('clientes/<int:pk>/', ClienteDetailView.as_view(), name='cliente_detail'),
    
    # Edición de cliente
    path('clientes/<int:pk>/edit/', ClienteUpdateView.as_view(), name='cliente_edit'),
    
    # Eliminación de cliente
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'),
    
    # Gestión de notas de cliente
    path('clientes/<int:pk>/add_note/', NoteCreateView.as_view(), name='add_note'),
    path('clientes/<int:cliente_pk>/eliminar-nota/<int:note_pk>/', DeleteNoteView.as_view(), name='delete_nota'),
    
    
    # Exportación de clientes
    path('clientes/exportar/<str:formato>/', ExportClientesView.as_view(), name='exportar_clientes'),
    
    # Generación de PDF de cliente
    path('clientes/<int:pk>/pdf/', ClientePDFView.as_view(), name='cliente_pdf'),
]