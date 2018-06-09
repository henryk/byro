from django.conf.global_settings import LANGUAGES
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class ByroConfiguration(SingletonModel):
    """ Use this class to build a configuration set that will automatically
    show up on the office settings interface. """

    class Meta:
        abstract = True


class Configuration(ByroConfiguration):

    name = models.CharField(
        null=True, blank=True,
        max_length=100,
        verbose_name=_('name'),
    )
    address = models.TextField(
        null=True, blank=True,
        max_length=500,
        verbose_name=_('address'),
    )
    url = models.CharField(
        null=True, blank=True,
        max_length=200,
        verbose_name=_('url'),
    )
    liability_interval = models.IntegerField(
        default=36,
        verbose_name=_('Liability interval'),
        help_text=_('For which interval should remaining fees be calculated?'),
    )

    language = models.CharField(
        choices=LANGUAGES,
        null=True, blank=True,
        max_length=5,
        verbose_name=_('language'),
    )
    currency = models.CharField(
        null=True, blank=True,
        max_length=3,
        verbose_name=_('currency'),
    )

    registration_form = JSONField(
        null=True, blank=True,
        verbose_name=_('registration form configuration'),
    )

    mail_from = models.EmailField(
        null=True, blank=True,
        max_length=100,
        verbose_name=_('e-mail sender address'),
    )

    form_title = _('General settings')

    backoffice_mail = models.EmailField(
        null=True, blank=True,
        max_length=100,
        verbose_name=_('e-mail of backoffice'),
    )

    welcome_member_template = models.ForeignKey(
        to='mails.MailTemplate',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    welcome_office_template = models.ForeignKey(
        to='mails.MailTemplate',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    leave_member_template = models.ForeignKey(
        to='mails.MailTemplate',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    leave_office_template = models.ForeignKey(
        to='mails.MailTemplate',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    fees_account = models.ForeignKey(
        to='bookkeeping.Account',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    donations_account = models.ForeignKey(
        to='bookkeeping.Account',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    fees_receivable_account = models.ForeignKey(
        to='bookkeeping.Account',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
