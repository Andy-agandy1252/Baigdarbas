from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('article/<str:article_link>/', views.scraped_article_detail, name='scraped_article_detail'),
    path('register/', views.register, name='register'),
    path('crypto/', views.crypto, name='crypto'),
    path('crypto/<id>/', views.crypto_detail, name='crypto_detail'),
    path('what_is_pro/', views.what_is_pro, name='what_is_pro'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('add_article/', views.add_article, name='add_article'),
    path('add_reklama/', views.add_reklama, name='add_reklama'),
    path('balanse/', views.balanse, name='balanse'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('about/', views.about, name='about'),
    path('feedback/', views.feedback, name='feedback'),
]
