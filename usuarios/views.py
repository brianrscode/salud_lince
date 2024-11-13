from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def login(request):
    return HttpResponse("Login de usuarios")

def medicos(request):
    return HttpResponse("Listado de medicos")

def pacientes(request):
    return HttpResponse("Listado de pacientes")