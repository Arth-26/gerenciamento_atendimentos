from rest_framework import serializers
from .models import Atendimentos, CustomUser, Medicos, Pacientes
from django.db import transaction
from django.utils import timezone

class UserMinimoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']
        read_only_fields = fields

    
class MedicoSerializer(serializers.ModelSerializer):
    user = UserMinimoSerializer(read_only=True, source='usuario')

    class Meta:
        model = Medicos
        fields = ['id', 'user', 'crm', 'especialidade']


class PacienteSerializer(serializers.ModelSerializer):
    user = UserMinimoSerializer(read_only=True, source='usuario')

    class Meta:
        model = Pacientes
        fields = ['id', 'user', 'cpf', 'data_nascimento']


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'type', 'password', 'is_active']
        read_only_fields = ['type']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Senha é obrigatória.'})
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class MedicoCreateSerializer(serializers.ModelSerializer):
    user = CustomUserCreateSerializer(source='usuario')

    class Meta:
        model = Medicos
        fields = ['id', 'user', 'crm', 'especialidade']

    def create(self, validated_data):
        user_data = validated_data.pop('usuario')

        with transaction.atomic():
            user = CustomUserCreateSerializer().create(user_data)
            user.type = CustomUser.Type.MEDICO
            user.save(update_fields=['type'])

            medico = Medicos.objects.create(usuario=user, **validated_data)

        return medico

    def update(self, instance, validated_data):
        user_data = validated_data.pop('usuario', None)
        if user_data:
            CustomUserCreateSerializer().update(instance.user, user_data)
        return super().update(instance, validated_data)


class PacienteCreateSerializer(serializers.ModelSerializer):
    user = CustomUserCreateSerializer(source='usuario')

    class Meta:
        model = Pacientes
        fields = ['id', 'user', 'cpf', 'data_nascimento']

    def create(self, validated_data):
        user_data = validated_data.pop('usuario')

        with transaction.atomic():
            user = CustomUserCreateSerializer().create(user_data)
            user.type = CustomUser.Type.PACIENTE
            user.save(update_fields=['type'])

            paciente = Pacientes.objects.create(usuario=user, **validated_data)

        return paciente

    def update(self, instance, validated_data):
        user_data = validated_data.pop('usuario', None)
        if user_data:
            CustomUserCreateSerializer().update(instance.user, user_data)
        return super().update(instance, validated_data)

    
class AtendimentosSerializer(serializers.ModelSerializer):
    medico_detalhe = serializers.StringRelatedField(source='medico', read_only=True)
    paciente_detalhe = serializers.StringRelatedField(source='paciente', read_only=True)

    medico = serializers.PrimaryKeyRelatedField(
        queryset=Medicos.objects.all(),
        write_only=True
    )
    paciente = serializers.PrimaryKeyRelatedField(
        queryset=Pacientes.objects.all(),
        write_only=True
    )

    class Meta:
        model = Atendimentos
        fields = ['id', 'medico', 'paciente', 'medico_detalhe', 'paciente_detalhe', 'data', 'descricao', 'cadastro_sistema', 'concluida']
        read_only_fields = ['id', 'paciente', 'cadastro_sistema']

    def validate_data_agendamento(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("A data do agendamento não pode ser no passado.")
        return value
