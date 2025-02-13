from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Redirige la raíz ("/") a "/crm/"
    path('', RedirectView.as_view(url='crm/', permanent=False)),
    path('crm/', include('crm.urls')),  # Aquí se agrupa el módulo CRM
]

# Agrega la ruta para servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
