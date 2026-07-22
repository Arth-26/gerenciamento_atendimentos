from django.db import models
from django.contrib.auth.models import AbstractUser, User

class CustomUser(AbstractUser):
    class Type(models.TextChoices):
        MEDICO = 'MEDICO', 'Médico'
        PACIENTE = 'PACIENTE', 'Paciente'

    type = models.CharField(
        max_length=50, choices=Type.choices, default=Type.PACIENTE, blank=True
    )

class Medicos(models.Model):
    class Especialidades(models.TextChoices):
        GERAL = 'GERAL', 'Geral'
        FISIOTERAPEUTA = 'FISIOTERAPEUTA', 'Fisioterapeuta'
        GINECOLOGISTA = 'GINECOLOGISTA', 'Ginecologista'
        UROLOGISTA = 'UROLOGISTA', 'Urologista'
        OFTALMOLOGISTA = 'OFTALMOLOGISTA', 'Oftalmologista'

    usuario = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='medico_profile', blank=True
    )
    crm = models.CharField(max_length=12, unique=True)
    especialidade = models.CharField(max_length=50, choices=Especialidades.choices, blank=True)

    def __str__(self):
        return f"{self.usuario.username}/{self.crm} - {self.especialidade}"

class Pacientes(models.Model):
    usuario = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='paciente_profile', blank=True
    )
    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()

    def __str__(self):
        return f"{self.usuario.username}/{self.cpf}"
    

# Create your models here.
class Atendimentos(models.Model):
    medico = models.ForeignKey(Medicos, on_delete=models.PROTECT, related_name='atendimentos')
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE, related_name='atendimentos')
    data = models.DateTimeField()
    descricao = models.TextField()
    cadastro_sistema = models.DateTimeField(auto_now_add=True)
    concluida = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.medico} -> {self.paciente}: {self.data.date()}'