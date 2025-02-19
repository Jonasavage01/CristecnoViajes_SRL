# urls.py
from django.urls import path
from .views import CRMView, ClienteDetailView, ClienteUpdateView, ClienteDeleteView
from .cliente_page import DocumentUploadView, NotesUpdateView

urlpatterns = [
    path('', CRMView.as_view(), name='crm_home'),
    path('clientes/<int:pk>/', ClienteDetailView.as_view(), name='cliente_detail'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('clientes/<int:pk>/edit/', ClienteUpdateView.as_view(), name='cliente_edit'),
    path('cliente/<int:pk>/upload-document/', DocumentUploadView.as_view(), name='upload_document'),
    path('cliente/<int:pk>/update-notes/', NotesUpdateView.as_view(), name='update_notes'),
    

    
]