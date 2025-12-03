# app/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_groups(sender, **kwargs):
    """Создаёт группы Client и Manager после миграций (если их ещё нет)."""
    from django.contrib.auth.models import Group
    Group.objects.get_or_create(name='Client')
    Group.objects.get_or_create(name='Manager')

class AppConfigDnDShop(AppConfig):
    name = 'app'
    verbose_name = "DnD Shop App"

    def ready(self):
        # подключаем сигнал post_migrate — группы будут создаваться после migrate
        post_migrate.connect(create_default_groups, sender=self)
