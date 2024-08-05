from .api import EmpleadoViewSet
from rest_framework.routers import DefaultRouter
from .views import EmpleadoDetailView
from django.urls import path

router = DefaultRouter()

router.register('api/empleados', EmpleadoViewSet, 'empleados')

urlpatterns = router.urls + [
    path('empleados/', EmpleadoDetailView.as_view(), name='empleado-list'),
    path('empleados/<int:pk>/', EmpleadoDetailView.as_view(), name='empleado-detail'),
]