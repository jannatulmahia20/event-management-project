from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')

    def __str__(self):
        return self.name

class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    email = models.EmailField()
    events = models.ManyToManyField(Event, related_name='participants')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



class RSVP(models.Model):
    ATTENDING = 'attending'
    NOT_ATTENDING = 'not_attending'
    MAYBE = 'maybe'
    STATUS_CHOICES = [
        (ATTENDING, 'Attending'),
        (NOT_ATTENDING, 'Not Attending'),
        (MAYBE, 'Maybe'),
    ]

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='rsvps')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ATTENDING)
    responded_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    comment = models.TextField(blank=True, null=True) 

    class Meta:
        unique_together = ('participant', 'event')

    def __str__(self):
        return f"{self.participant.name} - {self.event.name} ({self.status})"
