from datetime import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Atendimentos, CustomUser, Medicos, Pacientes


class BaseAtendimentoTestCase(APITestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='123456'    
        )

        self.medico_user = CustomUser.objects.create_user(
            username='medico_teste',
            email='medico1@example.com',
            password='123456',
            type='MEDICO'
        )
        self.medico = Medicos.objects.create(
            usuario = self.medico_user,
            crm='123456-SP',
            especialidade='GERAL'
        )

        self.paciente_user = CustomUser.objects.create_user(
            username='paciente_teste',
            email='paciente@example.com',
            password='123456',
            type='PACIENTE',
        )
        self.paciente = Pacientes.objects.create(
            usuario=self.paciente_user,
            cpf='12345678900',
            data_nascimento='1990-05-10',
        )

        self.outro_paciente_user = CustomUser.objects.create_user(
            username='maria_paciente',
            email='maria@example.com',
            password='senha12345',
            type='paciente',
        )
        self.outro_paciente = Pacientes.objects.create(
            usuario=self.outro_paciente_user,
            cpf='98765432100',
            data_nascimento='1985-02-20',
        )

        self.atendimento_1 = Atendimentos.objects.create(
            medico=self.medico,
            paciente=self.paciente,
            data=datetime(2026, 7, 30),
            descricao="Paciente relatou gripe severa"
        )
        self.atendimento_2 = Atendimentos.objects.create(
            medico=self.medico,
            paciente=self.outro_paciente,
            data=datetime(2026, 8, 1),
            descricao="Paciente relatou dores no peito"
        )


class MedicosViewSetTests(BaseAtendimentoTestCase):
    
    def test_lista_medicos_exige_autenticacao(self):
        url = reverse('medicos-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lista_medicos_autenticado_retorna_lista(self):
        self.client.force_authenticate(user=self.medico_user)
        url = reverse('medicos-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_criar_medico_somente_admin(self):
        self.client.force_authenticate(user=self.medico_user)
        url = reverse('medicos-list')
        payload = {
            "user": {
                "username": "Medico1",
                "email": "medico1@gmail.com",
                "password": "123456",
                "is_active": True
            },
            "crm": "123456-PB",
            "especialidade": "GERAL"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_criar_medico_admin_autenticado(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('medicos-list')
        payload = {
            "user": {
                "username": "Medico1",
                "email": "medico1@gmail.com",
                "password": "123456",
                "is_active": True
            },
            "crm": "123456-PB",
            "especialidade": "GERAL"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CustomUser.objects.filter(username='Medico1').exists()
        )
        self.assertTrue(
            Medicos.objects.filter(crm='123456-PB').exists()
        )


class PacientesViewSetTests(BaseAtendimentoTestCase):

    def test_lista_pacientes_exige_autenticacao(self):
        url = reverse('pacientes-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lista_pacientes_usuario_sem_permissao(self):
        self.client.force_authenticate(user=self.paciente_user)
        url = reverse('pacientes-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lista_pacientes_autenticado_retorna_lista(self):
        self.client.force_authenticate(user=self.medico_user)
        url = reverse('pacientes-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_criar_paciente_usuario_sem_permissao(self):
        self.client.force_authenticate(user=self.paciente_user)
        url = reverse('pacientes-list')
        payload = {
            "user": {
                "username": "Paciente1",
                "email": "paciente1@gmail.com",
                "password": "123456",
                "is_active": True
            },
            "cpf": "30030030030",
            "data_nascimento": "2003-12-11"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_criar_paciente_medico_autenticado(self):
        self.client.force_authenticate(user=self.medico_user)
        url = reverse('pacientes-list')
        payload = {
            "user": {
                "username": "Paciente1",
                "email": "paciente1@gmail.com",
                "password": "123456",
                "is_active": True
            },
            "cpf": "30030030030",
            "data_nascimento": "2003-12-11"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CustomUser.objects.filter(username='Paciente1').exists()
        )
        self.assertTrue(
            Pacientes.objects.filter(cpf='30030030030').exists()
        )


class AtendimentosViewSetTests(BaseAtendimentoTestCase):
    def test_lista_atendimentos_exige_autenticacao(self):
        url = reverse('atendimentos-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lista_atendimentos_retorna_lista(self):
        self.client.force_authenticate(user=self.medico_user)
        url = reverse('atendimentos-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_criar_atendimento_usuario_sem_permissao(self):
        self.client.force_authenticate(user=self.paciente_user)
        url = reverse('atendimentos-list')
        payload = {
            "medico": 1,
            "paciente": 1,
            "data": "2026-07-30",
            "descricao": "Paciente relatou gripe severa"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_criar_paciente_medico_autenticado(self):
        self.client.force_authenticate(user=self.medico_user)
        url = reverse('atendimentos-list')
        payload = {
            "medico": 1,
            "paciente": 1,
            "data": "2026-07-30",
            "descricao": "Paciente relatou gripe severa"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Atendimentos.objects.filter(medico=self.medico, paciente=self.paciente).exists()
        )

