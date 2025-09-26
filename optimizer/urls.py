from django.urls import path
from .views import run_optimizer

urlpatterns = [
    path('run/', run_optimizer, name='run-optimizer'),
]
