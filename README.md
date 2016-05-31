# django_basic_accounts
Some basic django accounts functions

#Basic Accounts Sys.

###Usage
1. add `url(r'^accounts/', include("accounts.urls", namespace="accounts")),` into `urls.py`
2. add `accounts` into `INSTALLED_APPS`
3. run `python manage.py makemigrations`
4. run `python manage.py migrate`

###Use captcha
1. set `USE_CAPTCHA = True`
2. add `captcha` into `INSTALLED_APPS`
3. add `url(r'^captcha/', include('captcha.urls')),` into `url.py`

###Use email
1. set `NEED_CONFIRM_EMAIL = True`
2. add `EMAIL_*` in `settings.py`

eg.
> `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'`
`EMAIL_PORT = 25`
`EMAIL_HOST = 'smtp.163.com'`
`EMAIL_HOST_USER = 'email_username@163.com'`
`EMAIL_HOST_PASSWORD = 'password'`


###Available functions
1. Register
2. Login
3. Logout
4. Change Password
5. Reset Password
6. Activate
7. Resend activate email

###Test
1. run `python manage.py test accounts` to test

###Todo
1. Log everything