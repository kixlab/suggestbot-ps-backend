"""suggestbot_annotator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from rest_framework.routers import DefaultRouter
from data.viewsets import LineViewSet
from base.viewsets import MomentViewSet, CreateUser, SurveyViewSet, LogViewSet, DeactivateUser
from rest_framework.authtoken import views

router = DefaultRouter()
router.register(r'lines', LineViewSet)
router.register(r'moments', MomentViewSet)
router.register(r'surveys', SurveyViewSet)
router.register(r'logs', LogViewSet)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('auth/', views.obtain_auth_token),
    path('register/', CreateUser.as_view()),
    path('deactivate/', DeactivateUser.as_view())

]
