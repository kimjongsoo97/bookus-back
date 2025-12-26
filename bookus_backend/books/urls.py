"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from . import views
from django.urls import path

app_name="books"
urlpatterns = [
    path('', views.book_list, name='book-list'),
    path('<int:pk>/', views.book_detail, name='book-detail'),
    path('search/',views.book_search,name='book-search'),
    path('favorite/',views.favorite,name='favorite'),
    path('random/',views.book_random_list,name='book-random-list')
]
