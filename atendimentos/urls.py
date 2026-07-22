from django.urls import path
from .views import AtendimentoViewSet, MedicoViewSet, PacienteViewSet

urlpatterns = [
    path('medicos/', MedicoViewSet.as_view(), name='medicos'),
    path('pacientes/', PacienteViewSet.as_view(), name='pacientes'),
    path('atendimentos/', AtendimentoViewSet.as_view(), name='atendimentos'),
]
