from django.urls import path
from .views import run_whatIf

urlpatterns = [
    path('run/', run_whatIf, name='run-whatIf'),
]
