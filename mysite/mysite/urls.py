from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pergale/', include('newsportal.urls')),
    path('', RedirectView.as_view(url='pergale/', permanent=True)),
]+ (static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) +
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
