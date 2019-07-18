from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from . import views
from django.urls import path

# API endpoints
urlpatterns = format_suffix_patterns([
    url(r'^api/user/login/$', obtain_auth_token, name='login-user'),
    url(r'^api/user/$', views.UserRegisterView.as_view(), name='register-user'),
    url(r'^favicon\.ico$',
        RedirectView.as_view(
            url='/static/icons/favicon.ico',
            permanent=True
        )),
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    path('api/dog/<pk>/<str:filter>/',
         views.UpdateDog.as_view(), name='change-dog'),
    path('api/dog/<pk>/<str:filter>/next/',
         views.DetailDog.as_view(), name='get-dog'),
    path('api/user/preferences/',
         views.RetrieveUpdateUserPref.as_view(), name='update-dog')
])
