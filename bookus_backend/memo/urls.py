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

app_name="memo"
urlpatterns = [
    path('',views.memo_index,name='memo_index'),
    path('create/',views.create_memo,name='memo_create'),
    path('update/<int:memo_id>/',views.update_memo,name='memo_update'),
    path('detail/<int:memo_id>/',views.detail_memo,name='memo_detail'),
    path('delete/<int:memo_id>/',views.delete_memo,name='memo_delete'),
    path('memo/audio/', views.create_memo_from_audio, name='create_memo_from_audio'),
    path('memo/<int:memo_id>/audio/', views.update_memo_from_audio, name='update_memo_from_audio')

]

