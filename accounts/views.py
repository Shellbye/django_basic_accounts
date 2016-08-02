# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.db import transaction
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from django.contrib import messages

from accounts.constants import NEED_CONFIRM_EMAIL, DOMAIN
from accounts.forms import UserRegisterForm, UserLoginForm, UserUpdateForm, UserResetPwdForm, UserForgetPwdForm, \
    UserChangePasswordForm
from accounts.utils import EmailThread


def index(request):
    return render(request, "accounts/index.html")


class UserRegisterView(View):
    @staticmethod
    @transaction.atomic
    def post(request):
        register_form = UserRegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save(NEED_CONFIRM_EMAIL)
            if NEED_CONFIRM_EMAIL:
                messages.success(request, u'注册成功,请到您的邮箱激活账号')
                return HttpResponseRedirect(reverse('accounts:index'))
            messages.success(request, u'注册成功,请登录')
            return HttpResponseRedirect(reverse('accounts:index'))
        else:
            return render(request, "accounts/form_tpl.html", {"form": register_form})

    @staticmethod
    def get(request):
        return render(request, "accounts/form_tpl.html", {"form": UserRegisterForm()})


def activate(request, username):
    user = User.objects.get(username=username)
    user.is_active = True
    user.save()
    messages.success(request, u'激活成功,请登录')
    return HttpResponseRedirect(reverse('accounts:index'))


def resend_activate(request, username):
    user = User.objects.get(username=username)
    email = user.email
    EmailThread(u"激活账号", u"点击 <a href='" + DOMAIN +
                reverse('accounts:activate', kwargs={'username': username}) +
                u"' >这里</a>激活您的账号", email).start()
    messages.success(request, u'激活邮件已发送,请登陆您的邮箱激活账号')
    return HttpResponseRedirect(reverse('accounts:index'))


class UserLoginView(View):
    @staticmethod
    def post(request):
        login_form = UserLoginForm(request.POST, request=request)
        if login_form.is_valid():
            user = authenticate(
                username=request.POST.get('username'),
                password=request.POST.get('password'),
            )
            if NEED_CONFIRM_EMAIL and not user.is_active:
                messages.success(request, u"账号需要激活, 请登陆您的邮箱激活, 或"
                                          u"点击<a href='" + DOMAIN +
                                 reverse('accounts:resend_activate',
                                         kwargs={'username': request.POST.get('username')}) +
                                 u"'>这里</a>重发激活邮件")
                return HttpResponseRedirect(reverse('accounts:index'))
            auth.login(request, user)
            messages.success(request, u'登录成功')
            if 'next' in request.GET:
                return HttpResponseRedirect(request.GET.get('next'))
            return HttpResponseRedirect(reverse('accounts:index'))
        else:
            return render(request, "accounts/form_tpl.html", {"form": login_form})

    @staticmethod
    def get(request):
        return render(request, "accounts/form_tpl.html", {"form": UserLoginForm()})


@login_required()
def logout(request):
    auth.logout(request)
    messages.success(request, u'成功退出')
    return HttpResponseRedirect(reverse('accounts:index'))


class UserDetailView(View):
    @staticmethod
    def post(request):
        update_form = UserUpdateForm(request.POST, instance=request.user)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, u'个人信息已更新')
            return HttpResponseRedirect(reverse('accounts:detail'))
        else:
            messages.error(request, u'信息更新失败')
            return render(request, "accounts/form_tpl.html",
                          {"form": update_form})

    @staticmethod
    def get(request):
        return render(request, "accounts/form_tpl.html",
                      {"form": UserUpdateForm(
                          instance=request.user)})


class UserChangePasswordView(View):
    @staticmethod
    def post(request):
        reset_form = UserChangePasswordForm(request.POST, request=request)
        if reset_form.is_valid():
            reset_form.reset()
            messages.success(request, u'密码修改成功,请重新登录')
            return HttpResponseRedirect(reverse('accounts:index'))
        else:
            return render(request, "accounts/form_tpl.html", {"form": reset_form})

    @staticmethod
    def get(request):
        return render(request, "accounts/form_tpl.html", {"form": UserChangePasswordForm()})


class ForgetPwdView(View):
    @staticmethod
    def post(request):
        forget_pwd_form = UserForgetPwdForm(request.POST)
        if forget_pwd_form.is_valid():
            messages.success(request, u'已发送重置密码连接,请登陆您的邮箱重置密码')
            return HttpResponseRedirect(reverse('accounts:index'))
        else:
            return render(request, "accounts/form_tpl.html", {"form": forget_pwd_form})

    @staticmethod
    def get(request):
        return render(request, "accounts/form_tpl.html", {"form": UserForgetPwdForm()})


class ResetPwdView(View):
    @staticmethod
    def post(request, code):
        update_pwd_form = UserResetPwdForm(request.POST)
        if update_pwd_form.is_valid():
            update_pwd_form.reset()
            messages.success(request, u'密码重置成功,请登录')
            return HttpResponseRedirect(reverse('accounts:index'))
        else:
            return render(request, "accounts/form_tpl.html", {"form": update_pwd_form})

    @staticmethod
    def get(request, code):
        return render(request, "accounts/form_tpl.html", {"form": UserResetPwdForm(initial={"code": code})})
