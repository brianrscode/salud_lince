from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ConsultaForm, SignosVitalesForm

@login_required
def crear_consulta(request):
    if not request.user.role.nombre_rol == 'medico':  # Verificar que el usuario sea médico
        messages.error(request, 'Solo los médicos pueden crear consultas.')
        return redirect('dashboard')  # Cambia esta URL según tu sistema

    if request.method == 'POST':
        consulta_form = ConsultaForm(request.POST)
        signos_form = SignosVitalesForm(request.POST)
        if consulta_form.is_valid() and signos_form.is_valid():
            consulta = consulta_form.save(commit=False)
            consulta.clave_medico = request.user  # Asignar el médico logueado
            consulta.save()

            signos_vitales = signos_form.save(commit=False)
            signos_vitales.consulta = consulta  # Asociar los signos vitales a la consulta
            signos_vitales.save()

            messages.success(request, 'La consulta y los signos vitales fueron creados exitosamente.')
            return redirect('medico_consultas')  # Cambia esta URL por la que prefieras
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        consulta_form = ConsultaForm()
        signos_form = SignosVitalesForm()

    return render(request, 'crear_consulta.html', {
        'consulta_form': consulta_form,
        'signos_form': signos_form
    })
