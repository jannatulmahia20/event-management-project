
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import Participant

User = get_user_model()

@receiver(post_save, sender=User)
def assign_participant_group(sender, instance, created, **kwargs):
    if created:
        participant_group, _ = Group.objects.get_or_create(name='Participant')
        instance.groups.add(participant_group)


@receiver(post_save, sender=User)
def create_participant(sender, instance, created, **kwargs):
    if created:
        Participant.objects.create(user=instance)
