"""shogi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
# from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('init_data', views.init_data, name='init_data'),
    path('legal_actions', views.legal_actions, name='legal_actions'),
    path('press_legal_actions', views.press_legal_actions, name='press_legal_actions'),

    # online game
    path('legal_actions_online', views.legal_actions_online, name='legal_actions_online'),
    path('check_win', views.check_win, name='check_win')
]
