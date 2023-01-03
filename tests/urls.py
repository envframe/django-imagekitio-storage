"""tests URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import TestFileFieldViewSet, TestFileAndImageFieldViewSet, TestWithoutMediaViewSet, \
    TestFileFieldVideoViewSet, TestThirdPartyFieldViewSet, index

routes = SimpleRouter()

# AUTHENTICATION
routes.register('api/v1/test-file', TestFileFieldViewSet, basename='test-1')
routes.register('api/v1/test-file-image', TestFileAndImageFieldViewSet, basename='test-2')
routes.register('api/v1/test-no-media', TestWithoutMediaViewSet, basename='test-3')
routes.register('api/v1/test-video', TestFileFieldVideoViewSet, basename='test-4')
routes.register('api/v1/test-third-party', TestThirdPartyFieldViewSet, basename='test-5')

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    *routes.urls
]
