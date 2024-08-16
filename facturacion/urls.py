from django.urls import path
from .views import FacturaCreateView, FacturaDeleteView, ClienteFacturasView, AdminFacturasView

urlpatterns = [
    path('api/v1/confirmar-factura/', FacturaCreateView.as_view(), name='crear_factura'),
    path('api/v1/eliminar-facturas/', FacturaDeleteView.as_view(), name='eliminar_factura'),
    path('api/v1/mis-facturas/', ClienteFacturasView.as_view(), name='mis_facturas'),
    path('api/v1/todas-facturas/', AdminFacturasView.as_view(), name='todas_facturas'),
]
