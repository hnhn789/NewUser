"""NewUser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from .views import SignUpView, LogoutView, LoginView, ResendView, ChangePasseordView

urlpatterns = [
    url(r'^email_confirmation/', include('email_confirm_la.urls', namespace='email_confirm_la')),
    url(r'^email_confirmation/resend/(?P<username>\w+)/', ResendView.as_view()),
    url(r'^admin/', admin.site.urls),
    url(r'^', admin.site.urls),
    url(r'^accounts/signup/', SignUpView.as_view()),
    url(r'^accounts/login/', LoginView.as_view()),
    url(r'^accounts/logout/', LogoutView.as_view()),
    url(r'^accounts/changepassword/', ChangePasseordView.as_view()),
]
