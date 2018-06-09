import pytest
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from byro.bookkeeping.models import Transaction, Booking, BookingType


@pytest.mark.django_db
def test_account_model_str(receivable_account):
    assert str(receivable_account) == "{} #{}".format(_('Asset account'), receivable_account.id)
    receivable_account.name = 'foo'
    assert str(receivable_account) == 'foo'


@pytest.mark.django_db
def test_account_methods(receivable_account):
    assert not receivable_account.bookings.all()
    assert receivable_account.total_debit(start=now()) == 0
    assert receivable_account.total_credit(start=now()) == 0


@pytest.mark.django_db
def test_transaction_balances(receivable_account, income_account):
    t = Transaction.objects.create(text='Beitrag wird fällig')
    for booking in [
            dict(amount=10, booking_type=BookingType.DEBIT, account=receivable_account),
            dict(amount=10, booking_type=BookingType.CREDIT, account=income_account)
    ]:
        Booking.objects.create(transaction=t, **booking)
    assert t.is_balanced()

@pytest.mark.django_db
def test_transaction_methods(receivable_account):
    t = Transaction.objects.create()
    t.debit(amount=10, account=receivable_account)
    t.save()

    assert t.total_credit() == 0
    assert t.total_debit() == 10
    assert not t.is_balanced()

@pytest.mark.django_db
def test_account_balances(bank_account, receivable_account, income_account):
    t1 = Transaction.objects.create(text='Beitrag wird fällig')
    t1.debit(amount=10, account=receivable_account),
    t1.credit(amount=10, account=income_account)
    t1.save()

    # FIXME Do something about that end=None,  (e.g. gain clarity about booking and value dates)
    assert income_account.balance(end=None) == 10
    assert receivable_account.balance(end=None) == 10

    t2 = Transaction.objects.create(text='Beitrag wird gezahlt')
    t2.debit(amount=10, account=bank_account)
    t2.credit(amount=10, account=receivable_account),
    t2.save()
    
    assert income_account.balance(end=None) == 10
    assert receivable_account.balance(end=None) == 0
    assert bank_account.balance(end=None) == 10

