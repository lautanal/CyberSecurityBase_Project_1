from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('addmessage/', views.addmessage, name='addmessage'),
    path('readmessage/<int:noteid>', views.readmessage, name='readmessage'),
    path('deletemessage/<int:noteid>', views.deletemessage, name='deletemessage'),
    path('searchmessage/', views.searchmessage, name='searchmessage'),
]