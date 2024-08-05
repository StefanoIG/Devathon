# Devathon

Devathon Grupo#3

## Manejo del proyecto

- Crear un proyecto: django-admin startproject nombre_proyecto .
- Crear un entorno virtual: python -m venv nombre_entorno
- Activar un entorno virtual: source nombre_entorno/bin/activate o .\env\bin\activate
- Desactivar un entorno virtual: deactivate
- Crear una aplicación: python manage.py startapp nombre_app
- Instalar django rest framework: pip install djangorestframework
- Instalar jwt: pip install djangorestframework_simplejwt
- Instalar psycopg(adaptador de conexiones a BD Postgres para Python): pip install psycopg
- Consultar paquetes instalados en el entorno virtual: pip list
- Instalar paquete de consulta de endpoints: pip install django-extensions y añadir `'django_extensions'` a `INSTALLED_APPS` en `settings.py`
- Consultar endpoints: python manage.py show_urls

## Manejo de entornos virtuales

- Instalar Django: pip install django
- Instalar un paquete: pip install nombre_paquete
- Crear un superusuario: python manage.py createsuperuser

## Manejo del servidor

- Arrancar el servidor: python manage.py runserver

## Migraciones

- Crear una migración: python manage.py makemigrations
- Aplicar una migración: python manage.py migrate

## Creación de app, modelo, serializador, vista y urls

- Crear una app: python manage.py startapp nombre_app
- Crear un modelo: en models.py
- Crear un serializador: en serializers.py
- Crear una vista: en views.py
- Crear una url: en urls.py
- Añadir la app a `INSTALLED_APPS` en `settings.py`
- Añadir la url a `urlpatterns` en `urls.py`, ejemplo: `path('api/', include('nombre_app.urls'))`

## Generar y uso de Documentación

- Dependencias
  pip install jsonschema==2.6
  pip install drf-spectacular
- Uso
  http://127.0.0.1:8000/api/schema/swagger-ui/
