from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import MicrosoftLoginView, MicrosoftLogin

urlpatterns = [
    path('', MicrosoftLoginView.as_view(), name="home"),
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls')),
    path('microsoft/', include('microsoft.urls')),
    path('accounts/', include('accounts.urls')),
    path('login/', MicrosoftLogin, name="MicrosoftLogin"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
