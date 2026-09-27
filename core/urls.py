from django.urls import re_path
from .views import hello_world, login_view, auth_view, register_view

urlpatterns = [
    re_path(r'^hello/?$', hello_world, name='hello_world'),
    re_path(r'^login/?$', login_view, name='login'),
    re_path(r'^auth/?$', auth_view, name='auth'),
    re_path(r'^register/?$', register_view, name='register'),
]
