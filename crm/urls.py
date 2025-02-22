from django.urls import path
from .cliente_page import ClienteDetailView, ClienteUpdateView, DocumentUploadView, NotesUpdateView, NoteCreateView,  DocumentDeleteView
from .views import CRMView, ClienteDeleteView

urlpatterns = [
    path('', CRMView.as_view(), name='crm_home'),
    
    # Ruta de edición (NUEVA)
    path('clientes/<int:pk>/edit/', ClienteUpdateView.as_view(), name='cliente_edit'),
    
    # Otras rutas específicas

     path('documentos/<int:pk>/eliminar/', DocumentDeleteView.as_view(), name='delete_document'),

    
    path('clientes/<int:pk>/add_note/', NoteCreateView.as_view(), name='add_note'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('clientes/<int:pk>/subir-documento/', DocumentUploadView.as_view(), name='upload_document'),
    
    # Ruta detalle del cliente (DEBE estar al final)
    path('clientes/<int:pk>/', ClienteDetailView.as_view(), name='cliente_detail'),
]