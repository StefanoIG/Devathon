"""
URL configuration for devathon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView,PasswordResetRequestAPI, PasswordResetConfirmAPI  # Asegúrate de importar la vista personalizada

urlpatterns = [
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/password_reset/', PasswordResetRequestAPI.as_view(), name='password_reset'),
    path('api/password_reset_confirm/', PasswordResetConfirmAPI.as_view(), name='password_reset_confirm'),
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('', include('empleados.urls')),
    path('', include('mesas.urls')),
    path('', include('reservas.urls')),
    path('', include('facturacion.urls')),
]
