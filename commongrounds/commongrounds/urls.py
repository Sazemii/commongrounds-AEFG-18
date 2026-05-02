from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('bookclub/', include('bookclub.urls')),
    path('commissions/', include('commissions.urls')),
    path('diyprojects/', include('diyprojects.urls')),
    path('merchstore/', include('merchstore.urls')),
    path('localevents/', include('localevents.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
