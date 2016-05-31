from django.db import models


class ForgetPassword(models.Model):
    USED = 1
    UNUSED = 0
    STATUS_CHOICES = (
        (USED, 1),
        (UNUSED, 0),
    )
    email = models.EmailField()
    code = models.CharField(max_length=500)
    status = models.IntegerField(choices=STATUS_CHOICES)

    def __unicode__(self):
        return self.email + "[" + str(self.status) + "]"

    def mark_used(self):
        self.status = ForgetPassword.UNUSED
        self.save()
