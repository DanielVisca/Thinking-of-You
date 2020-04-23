
from django.urls import path
from . import views

urlpatterns = [
    path('init',views.init, name='init'),
    path('send_toy',views.send_toy, name='send_toy'),
    path('logoff', views.logoff, name='logoff'),
    path('signup', views.signup, name='signup')
]
