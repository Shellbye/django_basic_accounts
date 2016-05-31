# -*- coding: utf-8 -*-
import hashlib
import threading

import time
from django.conf import settings
from django.core.mail import EmailMessage
from constants import NEED_CONFIRM_EMAIL

if NEED_CONFIRM_EMAIL:
    if settings.EMAIL_HOST_USER:
        email_host_user_available = True
    else:
        settings.EMAIL_HOST_USER = None
        email_host_user_available = False
        raise EnvironmentError("EMAIL_HOST_USER not config")


def send_email(subject, message, to):
    if not email_host_user_available:
        raise ImportError("No EMAIL_HOST_USER found in settings.")
    msg = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [to])
    msg.content_subtype = "html"
    msg.send()


def generate_code(user_id=None, **kwargs):
    seed = str(user_id) + str(time.time())
    for key, value in kwargs.iteritems():
        seed += str(value)
    return hashlib.md5(str(seed)).hexdigest().upper()


class EmailThread(threading.Thread):
    def __init__(self, subject, message, to):
        threading.Thread.__init__(self)
        self.subject = subject
        self.message = message
        self.to = to

    def run(self):
        self.performance()

    def performance(self):
        send_email(self.subject, self.message, self.to)
