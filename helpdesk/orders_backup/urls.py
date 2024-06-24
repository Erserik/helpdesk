from django.urls import path
from .views import submit_order, order_history, order_detail, active_orders, update_order_status
from django.conf import settings
from django.conf.urls.static import static
app_name = 'orders'
urlpatterns = [
    path('submit/', submit_order, name='submit_order'),
    path('history/', order_history, name='order_history'),
    path('detail/<int:pk>/', order_detail, name='order_detail'),
    path('active-orders/', active_orders, name='active_orders'),
    path('order/<int:pk>/update-status/', update_order_status, name='update_order_status'),

              ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
