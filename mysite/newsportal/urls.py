from django.urls import path
from .import views
from .views import crypto, crypto_detail
urlpatterns = [
    path('', views.index, name='index'),
    path('article/<path:article_link>/', views.article_detail, name='article_detail'),
    path('register/', views.register, name='register'),
    path('crypto/', views.crypto, name='crypto'),
    path('crypto/<id>/', views.crypto_detail, name='crypto_detail'),







    # path('news/', views.news, name='news'),cd mysite
    # path('markets/', views.markets, name='markets'),
    # path('pro/', views.pro, name='pro'),
    # path('signin/', views.signin, name='signin'),
    # path('signup/', views.signup, name='signup'),
]

