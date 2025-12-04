from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.user.models import TrustBadge, User

@receiver(post_save, sender=User)
def create_trust_badge(sender, instance, created, **kwargs):
    if created:
        TrustBadge.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_trust_badge(sender, instance, **kwargs):
    """Ensure badge is saved when user is updated"""
    if hasattr(instance, 'badge'):
        instance.badge.save()
