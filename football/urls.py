from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('fields/', fields, name='fields'),
    path('fields/<int:pk>/', field_detail, name='field_detail'),
    path('fields/<int:pk>/book/', book_field, name='book_field'),
    path('my-fields/', my_fields, name='my_fields'),
    path('my-fields/<int:pk>/cancel/', cancel_booking, name='cancel_booking'),
    path('my-fields/<int:pk>/finish/', finish_booking, name='finish_booking'),
    path('play-together/', play_together, name='play_together'),
    path('play-together/<int:pk>/join/', join_booking, name='join_booking'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('users/<int:pk>/', user_profile, name='user_profile'),
]