from django.urls import path
from .cliente_page import ClienteDetailView, ClienteUpdateView, DocumentUploadView, NotesUpdateView, NoteCreateView
from .views import CRMView, ClienteDeleteView

urlpatterns = [
    path('', CRMView.as_view(), name='crm_home'),
    path('clientes/<int:pk>/', ClienteDetailView.as_view(), name='cliente_detail'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('clientes/<int:pk>/edit/', ClienteUpdateView.as_view(), name='cliente_edit'),
    path('clientes/<int:pk>/upload_document/', DocumentUploadView.as_view(), name='upload_document'),
    path('clientes/<int:pk>/add_note/', NoteCreateView.as_view(), name='add_note'),
]