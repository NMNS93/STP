from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'add_patient', views.add_patient, name='add_patient'),
    url(r'patient_list', views.PatientListView.as_view(), name='patient_list')
    #url(r'^$', views.index, name='index'),
    #url(r'login', views.login, name='login')
    #url(r'logout', views.logout, name='logout')
]