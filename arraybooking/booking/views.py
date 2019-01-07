from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse

from .models import Patient, Array
from .forms import AddPatientForm

# Create your views here.
"""
Design:
- View for user login
- View for current Array patient list.
    - Add patients
    - Delete patients
"""

# @login_required
# def index(request):
#     context = None
#     return render(request, 'booking/index.html', context)


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'booking/index.html'
    context_object_name = 'booked_arrays'

    def get_queryset(self):
        """Return all Booked in Arrays"""
        return Array.objects.all()

@login_required
def add_patient(request):
    if request.method == "POST":
        form = AddPatientForm(request.POST)
        if form.is_valid():
            new_patient = form.save()
            if 'check_array' in request.POST.keys():
                new_array = Array(patient=new_patient)
                new_array.save()
            return redirect('index')
    else:
        form = AddPatientForm()
        return render(request, 'booking/add_patient.html', {'form':form})

class PatientListView(LoginRequiredMixin, generic.ListView):
    template_name = 'booking/patient_list.html'
    context_object_name = 'patients'

    def get_queryset(eslf):
        """Return all Patients"""
        return Patient.objects.all()

