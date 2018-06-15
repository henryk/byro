from django.contrib.postgres.fields import JSONField
from django.db import models, transaction
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
            (cls.DEBIT, _('Debit')),
            (cls.CREDIT, _('Credit')),
        )


class Transaction(Auditable, models.Model):
    booking_datetime = models.DateTimeField(null=True)
    value_datetime = models.DateTimeField(null=True)

    memo = models.CharField(max_length=1000, null=True, blank=True)

    data = JSONField(null=True)

    reverses = models.ForeignKey(
        to='transaction',
        on_delete=models.PROTECT,
        null=True,
    )

    @property
    def debits(self):
        return self.bookings.filter(booking_type=BookingType.DEBIT)

    @property
    def credits(self):
        return self.bookings.filter(booking_type=BookingType.CREDIT)

    def total_credit(self):
        return self.credits.aggregate(total=models.Sum('amount'))['total'] or 0

    def total_debit(self):
        return self.debits.aggregate(total=models.Sum('amount'))['total'] or 0

    def is_balanced(self):
        return self.total_credit() == self.total_debit()

    def debit(self, *args, **kwargs):
        return Booking.objects.create(transaction=self, booking_type=BookingType.DEBIT, *args, **kwargs)

    def credit(self, *args, **kwargs):
        return Booking.objects.create(transaction=self, booking_type=BookingType.CREDIT, *args, **kwargs)

    @classproperty
    def with_balance(cls):
        qs = cls.objects.all()
        qs = qs.annotate(
            transaction_balance=models.Sum(
                models.Case(
                    models.When(bookings__booking_type=BookingType.DEBIT, then="bookings__amount"),
                    models.When(bookings__booking_type=BookingType.CREDIT, then=0-models.F("bookings__amount")),
                    output_field=models.IntegerField()
                )
            )
        )
        return qs

    @classproperty
    def unbalanced_transactions(cls):
        return cls.with_balance.exclude(transaction_balance=0)

    def find_memo(self):
        if self.memo:
            return self.memo
        booking = self.bookings.exclude(memo=None).first()
        if booking:
            return booking.memo
        return None

    @transaction.atomic
    def process_transaction(self):
        """
        Collects responses to the signal `process_transaction`. Raises an
        exception if multiple results were found, and re-raises received Exceptions.

        Returns a list of one or more VirtualTransaction objects if no Exception
        was raised.
        """
        from byro.bookkeeping.signals import process_transaction
        responses = process_transaction.send_robust(sender=self)
        if len(responses) > 1:
            raise Exception('More than one plugin tried to derive virtual transactions: {}'.format([r[0].__module__ + '.' + r[0].__name__ for r in responses]))
        if len(responses) < 1:
            raise Exception('No plugin tried to derive virtual transactions.')
        receiver, response = responses[0]

        if isinstance(response, Exception):
            raise response

        if not isinstance(response, list) or len(response) == 0:
            raise Exception('Transaction could not be matched')

        return response  # TODO: sanity check response for virtual transaction objects


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
    memo = models.CharField(max_length=1000, null=True)
    amount = models.DecimalField(
        max_digits=8, decimal_places=2,  # TODO: enforce min_value = 0
    )
    data = JSONField(null=True)
    importer = models.CharField(null=True, max_length=500)
    source = models.ForeignKey(
        to="bookkeeping.RealTransactionSource",
        on_delete=models.PROTECT,
        related_name='bookings',
        null=True,
    )

    def __str__(self):
        return "{amount} {booking_type} {account}".format(
            amount=self.amount,
            booking_type=self.booking_type,
            account=self.account,
        )

    def find_memo(self):
        if self.memo:
            return self.memo
        return self.transaction.find_memo()

    @property
    def counter_bookings(self):
        if self.booking_type == BookingType.CREDIT:
            return self.transaction.debits.prefetch_related('account')
        elif self.booking_type == BookingType.DEBIT:
            return self.transaction.credits.prefetch_related('account')
        return None
