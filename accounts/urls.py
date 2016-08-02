# -*- coding: utf-8 -*-
from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^register/$', UserRegisterView.as_view(), name="register"),
    url(r'^activate/(?P<username>.*)/$', activate, name="activate"),
    url(r'^resend_activate/(?P<username>.*)/$', resend_activate, name="resend_activate"),
    url(r'^login/$', UserLoginView.as_view(), name="login"),
    url(r'^logout/$', logout, name="logout"),
    url(r'^detail/$', login_required(UserDetailView.as_view()), name="detail"),
    url(r'^change_pwd/$', login_required(UserChangePasswordView.as_view()), name="change_pwd"),
    url(r'^forget_pwd/$', ForgetPwdView.as_view(), name="forget_pwd"),
    url(r'^reset_pwd/(?P<code>.*)/$', ResetPwdView.as_view(), name="reset_pwd"),
]
