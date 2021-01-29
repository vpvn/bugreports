'''
Bugreports models
=================

'''

import uuid
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from . import managers


OS_CHOICES = [
    (None, 'Not specified'),
    ('android', 'Android'),
    ('win', 'Windows'),
    ('linux', 'Linux'),
]


class BuggyProject(models.Model):
    '''Model for project definition.

    All bugs are related to project, where it occurs.
    '''

    # Relations
    # Attributes - Mandatory
    id = models.CharField(
        verbose_name='project unique id',
        primary_key=True,
        max_length=20,
    )
    '''Project must have manually entered unique id.
    '''

    name = models.CharField(
        verbose_name='name',
        max_length=150,
    )

    # Attributes - Optional

    # Object Manager
    objects = managers.BuggyProjectManager()

    # Custom Properties
    # Method

    class Meta:
        verbose_name = 'project'
        verbose_name_plural = 'projects'

    def __str__(self):
        return ('{name}').format(
                                  name=self.name,
                                  )


class Bug(models.Model):
    '''Model for bug, that related to the project.

    Bug has 'occasions'. Each time the bug occurs
    new occasion related to the bug created.
    '''

    # Relations
    project = models.ForeignKey(
        BuggyProject,
        on_delete=models.CASCADE,
        related_name='bugs',
        verbose_name='project',
    )

    # Attributes - Mandatory
    buguuid = models.UUIDField(
        verbose_name='exception uuid',
        editable=False,
        blank=True,
        unique=True,
    )
    '''buguuid is a uuid which is based on the project name and the exception text
       it's calculated in the `pre_save` signal
    '''

    exception_text = models.TextField(
        verbose_name='exception text',
    )

    # Attributes - Optional
    ts_add = models.DateTimeField(
       verbose_name='creation timestamp',
       auto_now_add=True,
    )

    description = models.TextField(
        verbose_name='description',
        blank=True,
        default='',
    )

    discussian_url = models.URLField(
        verbose_name='discussian url',
        blank=True,
        default='',
    )

    # Object Manager
    objects = managers.BugManager()

    # Custom Properties
    # Method

    class Meta:
        ordering = ('ts_add',)
        verbose_name = 'bug'
        verbose_name_plural = 'bugs'

    def __str__(self):
        return ('{buguuid} (has {occasions_cnt} occasions)').format(
            buguuid=self.buguuid,
            occasions_cnt=self.occasions.count(),
        )


class Occasion(models.Model):
    '''Model of ocassion, that related to the bug.

    Each time the bug occurs we register it in this model.
    Gathering information that can help us to clarify the chain of
    bug causality.
    '''

    # Relations
    bug = models.ForeignKey(
        Bug,
        on_delete=models.CASCADE,
        related_name='occasions',
        verbose_name='bug',
    )

    # Attributes - Mandatory
    ts_add = models.DateTimeField(
        verbose_name='creation timestamp',
        auto_now_add=True,
    )

    # Attributes - Optional
    email = models.EmailField(
        verbose_name='consumer email',
        blank=True,
        null=True,
    )

    ip = models.GenericIPAddressField(
        verbose_name='ip',
        blank=True,
        null=True,
    )

    os = models.CharField(
        verbose_name='OS',
        choices=OS_CHOICES,
        max_length=10,
        blank=True,
        null=True,
    )

    details = models.TextField(
        verbose_name='details',
        blank=True,
        null=True,
    )

    # Object Manager
    objects = managers.OccusianManager()

    # Custom Properties
    # Method

    class Meta:
        ordering = ('-ts_add',)
        verbose_name = 'occasion'
        verbose_name_plural = 'occasions'

    def __str__(self):
        return ('{bug}: {os} {ip}').format(
            os=self.os,
            ip=self.ip,
            bug=self.bug,
        )


def buguuid(project_id, exception_text):
    return uuid.uuid5(
        uuid.uuid5(uuid.NAMESPACE_X500, project_id),
        exception_text
    )


@receiver(pre_save, sender=Bug)
def update_buguuid(sender, instance, using, **kwargs):
    instance.buguuid = buguuid(
        instance.project_id,
        instance.exception_text
    )
