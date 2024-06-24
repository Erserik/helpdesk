from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
app_name = 'orders'
urlpatterns = [
    path('submit/', submit_order, name='submit_order'),
    path('history/', order_history, name='order_history'),
    path('detail/<int:pk>/', order_detail, name='order_detail'),
    path('active-orders/', active_orders, name='active_orders'),
    path('my-orders/', my_orders, name='my_orders'),
    path('order/<int:pk>/update-status/', update_order_status, name='update_order_status'),
    path('order/<int:pk>/send_message/', send_message, name='send_message'),
    path('reports/', reports, name='reports'),
    path('download/<int:order_id>/', download_order_report, name='download_order_report'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
