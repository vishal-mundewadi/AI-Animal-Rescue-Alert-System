from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

class AnimalReport(models.Model):
    ANIMAL_CHOICES = [
        ('Dog', 'Dog'), 
        ('Cat', 'Cat'), 
        ('Bird', 'Bird'),
        ('Snake', 'Snake'), 
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Acknowledged', 'Acknowledged'),
        ('Resolved', 'Resolved'),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    animal_type = models.CharField(max_length=50, choices=ANIMAL_CHOICES, default='Other')
    description = models.TextField()
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='reports/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.animal_type} at {self.location}"


class NGO(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.email or self.phone})"


# --- Notify NGOs when a new report is created ---
@receiver(post_save, sender=AnimalReport)
def notify_ngos(sender, instance, created, **kwargs):
    if created:
        ngos = NGO.objects.filter(is_active=True)
        subject = f"🚨 New Rescue Report: {instance.animal_type}"
        message = f"""
        A {instance.animal_type} needs help!

        📍 Location: {instance.location}
        📝 Description: {instance.description}

        Please respond and update the status to 'Acknowledged' once received.
        """
        from_email = 'muvishal14@gmail.com'
        recipient_list = [ngo.email for ngo in ngos if ngo.email]

        if recipient_list:
            send_mail(subject, message, from_email, recipient_list)


# --- Notify user when NGO updates status ---
@receiver(post_save, sender=AnimalReport)
def notify_user_status_change(sender, instance, created, **kwargs):
    if not created:  # means record was updated
        try:
            # fetch previous record before save
            old_instance = AnimalReport.objects.get(pk=instance.pk)
        except AnimalReport.DoesNotExist:
            return

        # only send mail if status actually changed
        if old_instance.status != instance.status:
            subject, message = None, None

            if instance.status == 'Acknowledged':
                subject = f"✅ Rescue Team Acknowledged Your Report"
                message = (
                    f"Dear {instance.name},\n\n"
                    f"The rescue team has acknowledged your report for the {instance.animal_type}.\n"
                    f"They are on their way to the location: {instance.location}\n\n"
                    f"Thank you for helping save animals! 🐾"
                )

            elif instance.status == 'Resolved':
                subject = f"🎉 Rescue Completed for {instance.animal_type}"
                message = (
                    f"Dear {instance.name},\n\n"
                    f"The rescue operation for the {instance.animal_type} you reported has been successfully completed.\n"
                    f"Thank you for your compassion and support. 💚"
                )

            if subject and message:
                from_email = 'muvishal14@gmail.com'
                recipient_list = [instance.email]
                send_mail(subject, message, from_email, recipient_list)
