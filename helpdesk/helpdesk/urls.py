from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import MicrosoftLoginView, MicrosoftLogin

app_name = "main"

urlpatterns = [
    path('', MicrosoftLogin, name="home"),
    path('admin/', admin.site.urls),
    path('microsoft/', include('microsoft.urls')),
    path('accounts/', include('accounts.urls')),
    path('login/', MicrosoftLoginView.as_view(), name="MicrosoftLogin"),
]

urlpatterns += i18n_patterns(
    path('orders/', include('orders.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)





