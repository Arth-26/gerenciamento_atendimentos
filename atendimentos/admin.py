from django.contrib import admin
from .models import Atendimentos, Medicos, Pacientes

admin.site.register(Medicos)
admin.site.register(Pacientes)
admin.site.register(Atendimentos)