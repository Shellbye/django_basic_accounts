# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserChangeForm

from accounts.constants import DOMAIN
from accounts.models import ForgetPassword
from accounts.utils import EmailThread, generate_code

from constants import USE_CAPTCHA

if USE_CAPTCHA:
    from captcha.fields import CaptchaField

    captchaField = CaptchaField(required=True, label="验证码",
                                error_messages={'required': '验证码必须填写', 'invalid': '验证码错误'})


class UserRegisterForm(forms.Form):
    username = forms.CharField(required=True, label="用户名")
    password = forms.CharField(required=True, min_length=6, label="密码", widget=forms.PasswordInput)
    email = forms.EmailField(required=True, label="邮箱")
    if USE_CAPTCHA:
        captcha = captchaField

    def clean_username(self):
        # check if the username is used already
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username %(username)s has been used!",
                                        params={'username': username}, )
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email %(email)s has been used!",
                                        params={'email': email}, )
        return email

    def save(self, need_confirm_email):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        user = User.objects.create_user(
            username,
            email,
            self.cleaned_data['password'],
        )
        if need_confirm_email:
            user.is_active = False
            user.save()
            EmailThread(u"激活账号", u"点击 <a href='" + DOMAIN +
                        reverse('accounts:activate', kwargs={'username': username}) +
                        u"' >这里</a>激活您的账号", email).start()


class UserLoginForm(forms.Form):
    username = forms.CharField(required=True, label="用户名")
    password = forms.CharField(required=True, min_length=6, label="密码", widget=forms.PasswordInput)
    if USE_CAPTCHA:
        captcha = captchaField

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(UserLoginForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        # check if the username is used already
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(u"用户名 %(username)s 不存在",
                                        params={'username': username}, )
        return username

    def clean(self):
        if self.errors:
            return
        username = self.cleaned_data['username']
        user = authenticate(
            username=username,
            password=self.cleaned_data['password'],
        )
        if user is None:
            raise forms.ValidationError(u"密码错误")


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email')
        help_texts = {
            'username': None,
        }

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        del self.fields['password']


class UserChangePasswordForm(forms.Form):
    old_password = forms.CharField(required=True, widget=forms.PasswordInput)
    new_password = forms.CharField(required=True, widget=forms.PasswordInput)
    new_password_2 = forms.CharField(required=True, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(UserChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        user = authenticate(
            username=self.request.user.username,
            password=self.cleaned_data['old_password'],
        )
        if user is None:
            raise forms.ValidationError(u"原密码不正确")

    def clean(self):
        if self.cleaned_data['new_password'] != self.cleaned_data['new_password_2']:
            raise forms.ValidationError(u"两次输入的密码不一致")

    def reset(self):
        self.request.user.set_password(self.cleaned_data['new_password'])
        self.request.user.save()
        auth.logout(self.request)


class UserForgetPwdForm(forms.Form):
    email = forms.EmailField(required=True, label="注册的邮件地址")

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("The email is not registered")
        user = User.objects.get(email=email)
        f_pwd = ForgetPassword.objects.create(email=email, code=generate_code(),
                                              status=ForgetPassword.UNUSED)
        EmailThread(u"重置密码", u"亲爱的用户" + user.username + u", 点击<a href='" + DOMAIN +
                    reverse('accounts:reset_pwd', kwargs={'code': f_pwd.code}) +
                    u"'>这里</a>重置您的密码", email).start()
        return email


class UserResetPwdForm(forms.Form):
    code = forms.CharField(widget=forms.HiddenInput)
    new_password = forms.CharField(required=True, widget=forms.PasswordInput, label="输入新密码", min_length=6)
    new_password_2 = forms.CharField(required=True, widget=forms.PasswordInput, label="再次输入新密码", min_length=6)

    def __init__(self, *args, **kwargs):
        super(UserResetPwdForm, self).__init__(*args, **kwargs)
        self.email = None

    def clean(self):
        if self.errors:
            return
        if self.cleaned_data['new_password'] != self.cleaned_data['new_password_2']:
            raise forms.ValidationError(u"两次输入的密码不一致")
        code = self.cleaned_data['code']
        forget_pwd = ForgetPassword.objects.get(code=code)
        if forget_pwd is None:
            raise forms.ValidationError(u"错误的验证码")
        elif forget_pwd.status != ForgetPassword.UNUSED:
            raise forms.ValidationError(u"验证码已使用")
        else:
            forget_pwd.mark_used()
        self.email = forget_pwd.email

    def reset(self):
        user = User.objects.get(email=self.email)
        user.set_password(self.cleaned_data['new_password'])
        user.save()
