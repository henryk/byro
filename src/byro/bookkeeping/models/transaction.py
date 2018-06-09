from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.decorators import classproperty
from django.utils.translation import ugettext_lazy as _

from byro.common.models.auditable import Auditable
from byro.common.models.choices import Choices


class BookingType(Choices):
    DEBIT = 'debit'
    CREDIT = 'credit'

    @classproperty
    def choices(cls):
        return (
            (cls.DEBIT, _('Soll')),
            (cls.CREDIT, _('Haben')),
        )


class Transaction(Auditable, models.Model):
    booking_datetime = models.DateTimeField(null=True)
    value_datetime = models.DateTimeField(null=True)

    text = models.CharField(max_length=1000)

    data = JSONField(null=True)

    reverses = models.ForeignKey(
        to='transaction',
        on_delete=models.PROTECT,
        null=True,
    )

    def total_credit(self):
        return self.bookings.filter(booking_type=BookingType.CREDIT).aggregate(total=models.Sum('amount'))['total'] or 0

    def total_debit(self):
        return self.bookings.filter(booking_type=BookingType.DEBIT).aggregate(total=models.Sum('amount'))['total'] or 0

    def is_balanced(self):
        return self.total_credit() == self.total_debit()

    def debit(self, *args, **kwargs):
        return Booking.objects.create(transaction=self, booking_type=BookingType.DEBIT, *args, **kwargs)

    def credit(self, *args, **kwargs):
        return Booking.objects.create(transaction=self, booking_type=BookingType.CREDIT, *args, **kwargs)


class Booking(Auditable, models.Model):
    transaction = models.ForeignKey(
        to='bookkeeping.Transaction',
        related_name='bookings',
        on_delete=models.CASCADE,
        null=False,
    )
    account = models.ForeignKey(
        to='bookkeeping.Account',
        related_name='bookings',
        on_delete=models.CASCADE,
        null=False,
    )
    member = models.ForeignKey(
        to='members.Member',
        related_name='bookings',
        on_delete=models.CASCADE,
        null=True
    )
    booking_type = models.CharField(
        choices=BookingType.choices,
        max_length=BookingType.max_length,
        null=False, blank=False,
    )
    amount = models.DecimalField(
        max_digits=8, decimal_places=2,  # TODO: enforce min_value = 0
    )
    data = JSONField(null=True)
    importer = models.CharField(null=True, max_length=500)
