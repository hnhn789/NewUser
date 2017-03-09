from django.conf.urls import url, include
from django.contrib import admin

from accounts.views import SignUpView, LogoutView, LoginView, ResendView, ChangePasseordView

urlpatterns = [
    url(r'^email_confirmation/', include('email_confirm_la.urls', namespace='email_confirm_la')),
    url(r'^email_confirmation/resend/(?P<username>\w+)/', ResendView.as_view()),
    url(r'^signup/', SignUpView.as_view()),
    url(r'^login/', LoginView.as_view()),
    url(r'^logout/', LogoutView.as_view()),
    url(r'^changepassword/', ChangePasseordView.as_view()),

]