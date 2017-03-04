from django.contrib.auth.models import User

from django.dispatch import receiver
from email_confirm_la.signals import post_email_confirmation_confirm




@receiver(post_email_confirmation_confirm)
def post_email_confirmation_confirm_callback(sender, confirmation, **kwargs):
    model_instace = confirmation.content_object
    email = confirmation.email
    old_email = kwargs['old_email']

    # do_your_stuff()