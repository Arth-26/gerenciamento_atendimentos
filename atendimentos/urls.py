from django.urls import path
from .views import AtendimentoViewSet, MedicoViewSet, PacienteViewSet, hello_world

urlpatterns = [
    path('hello_world/', hello_world, name='hello-world')
]
