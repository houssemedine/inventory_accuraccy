from django.urls import path
from inventory_accuracy import views

urlpatterns = [
    
    path('upload/', views.upload_files, name='upload'),
    path('home/', views.home, name='home'),
    
]
