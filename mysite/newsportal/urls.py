from django.urls import path

from .import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('news/', views.news, name='news'),
    # path('markets/', views.markets, name='markets'),
    # path('pro/', views.pro, name='pro'),
    # path('signin/', views.signin, name='signin'),
    # path('signup/', views.signup, name='signup'),
]
