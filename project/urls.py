from django.urls import path
from . import views

urlpatterns = [
    # Frontend
    path('', views.home, name='home'),
    path('project/<int:project_id>/', views.project, name='project'),
    path('about/', views.about, name='about'),
] 