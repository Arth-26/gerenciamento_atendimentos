from django.http import JsonResponse
from rest_framework.views import APIView, PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets
from rest_framework import status
from rest_framework.validators import ValidationError

from atendimentos.permissions import OnlyAdminCreate

from .models import Atendimentos, CustomUser, Medicos, Pacientes
from .serializers import AtendimentosSerializer
from atendimentos import serializers


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CustomUserCreateSerializer
        elif self.action == 'list':
            return serializers.CustomUserListSerializer

        return serializers.CustomUserListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] 

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medicos.objects.all()
    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.MedicoCreateSerializer
        elif self.action == 'list':
            return serializers.MedicoSerializer

        return serializers.MedicoSerializer

    permission_classes = [IsAuthenticated, OnlyAdminCreate]

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Pacientes.objects.all()
    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.PacienteCreateSerializer
        elif self.action == 'list':
            return serializers.PacienteSerializer

        return serializers.PacienteSerializer
    
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Pacientes.objects.all()
        if self.request.user.is_superuser or hasattr(self.request.user, 'medico_profile'):
            return queryset
        else:
            raise PermissionDenied({
                'detail': 'Você não tem permissão para acessar essas informações!',
            })
        

    def perform_create(self, serializer):
        if self.request.user.is_superuser or hasattr(self.request.user, 'medico_profile'):
            serializer.save()
        else:
            raise PermissionDenied({
                'detail': 'Você não tem permissão para cadastrar um novo paciente.',
            })


class AtendimentoViewSet(viewsets.ModelViewSet):
    queryset = Atendimentos.objects.all()
    serializer_class = AtendimentosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Atendimentos.objects.all().select_related(
            'medico', 'paciente', 'medico__usuario', 'paciente__usuario'
        )
        if self.request.user.is_superuser:
            return queryset
        elif hasattr(self.request.user, 'medico_profile'):
            queryset.filter(medico=self.request.user.medico_profile)
        elif hasattr(self.request.user, 'paciente_profile'):
            queryset.filter(paciente=self.request.user.paciente_profile)
        else:
            raise PermissionDenied({
                'detail': 'Você não tem permissão para acessar essas informações!',
            })
        
        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'medico_profile'):
            serializer.save(medico=self.request.user.medico_profile)
        else:
            raise PermissionDenied({
                'detail': 'Apenas médicos podem criar atendimentos.',
            })



def hello_world(request):
    if request.method == 'GET':
        return JsonResponse({
            "message": "Hello World",
            "subdominio": request.get_host().split('.')[0]
        })