from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import MicrosoftLoginView, MicrosoftLogin

app_name = "main"

urlpatterns = [
    path('', MicrosoftLogin, name="home"),
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls')),
    path('microsoft/', include('microsoft.urls')),
    path('accounts/', include('accounts.urls')),
    path('login/', MicrosoftLoginView, name="MicrosoftLogin"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
