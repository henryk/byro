from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from byro.bookkeeping.models import Account, AccountCategory, Transaction, BookingType
from byro.common.models.configuration import Configuration
from byro.members.models import FeeIntervals, Member, Membership, MembershipType


def make_date(delta, end=False):
    date = (now() - delta).date()
    date = date.replace(day=1)
    if end:
        date = date + relativedelta(month=1)
        return date - timedelta(days=1)
    return date


class Command(BaseCommand):
    help = "Introduce test data, including members and payments"

    def create_configs(self):
        config = Configuration.get_solo()
        config.name = 'Der Verein DER VEREIN'
        config.address = 'Erich-Weinert-Straße 53\n39104 Magdeburg'
        config.url = 'https://dervereindervere.in'
        config.language = 'de'
        config.currency = 'EUR'
        config.mail_from = 'verein@dervereindervere.in'
        config.backoffice_mail = 'vorstanz@dervereindervere.in'
        config.save()

    def create_accounts(self):
        "Make sure there's at least one asset account that is not member fees receivable"
        account = self.bank_account
        if not account:
            Account.objects.create(
                account_category=AccountCategory.ASSET,
                name=_("Demo bank account")
            )

    @property
    def bank_account(self):
        config = Configuration.get_solo()
        return Account.objects\
            .filter(account_category=AccountCategory.ASSET)\
            .exclude(pk=config.fees_receivable_account.pk)\
            .first()

    def make_paid(self, member, vaguely=False, overly=False):
        config = Configuration.get_solo()
        member.update_liabilites()
        src_account = config.fees_receivable_account
        dst_account = self.bank_account
        for index, liability in enumerate(member.bookings.filter(account=src_account, booking_type=BookingType.DEBIT, transaction__value_datetime__lte=now()).all()):
            if vaguely and index % 2 == 0:
                continue
            amount=liability.amount if not overly else liability.amount * 2
            t = Transaction.objects.create(text=_("Fee is paid"), value_datetime=liability.transaction.value_datetime)
            t.debit(account=dst_account, member=member, amount=amount)
            t.credit(account=src_account, member=member, amount=amount)
            t.save()

    def create_membership_types(self):
        MembershipType.objects.create(name='Standard membership', amount=120)

    def create_members(self):
        has_left = Member.objects.create(
            number='1',
            name='Francis Foundingmember',
            address='Foo St 1\nSome Place',
            email='francis@group.org',
        )
        Membership.objects.create(
            member=has_left,
            start=make_date(relativedelta(years=2)),
            end=make_date(relativedelta(years=1), end=True),
            interval=FeeIntervals.MONTHLY,
            amount=10,
        )
        self.make_paid(has_left)
        does_not_pay = Member.objects.create(
            number='2',
            name='Yohnny Yolo',
            address='Bar St 1\nSome Distant Place',
            email='yolo@group.org',
        )
        Membership.objects.create(
            member=does_not_pay,
            start=make_date(relativedelta(years=2)),
            interval=FeeIntervals.MONTHLY,
            amount=10,
        )
        does_not_pay.update_liabilites()
        pays_occasionally = Member.objects.create(
            number='3',
            name='Olga Occasional',
            address='Currently unknown',
            email='olga@group.org',
        )
        Membership.objects.create(
            member=pays_occasionally,
            start=make_date(relativedelta(years=1, months=6)),
            interval=FeeIntervals.MONTHLY,
            amount=10,
        )
        self.make_paid(pays_occasionally, vaguely=True)
        pays_regularly = Member.objects.create(
            number='4',
            name='Dennis Diligent',
            address='Best St 3\nFoo Town\nMy Country\nEarth\nUniverse',
            email='dennis@group.org',
        )
        Membership.objects.create(
            member=pays_regularly,
            start=make_date(relativedelta(years=1, months=3)),
            interval=FeeIntervals.MONTHLY,
            amount=10,
        )
        self.make_paid(pays_regularly)
        pays_too_much = Member.objects.create(
            number='5',
            name='Omar Overachiever',
            address='SuperBest St 3\nSuperFoo Town',
            email='omar@group.org',
        )
        Membership.objects.create(
            member=pays_too_much,
            start=make_date(relativedelta(years=1)),
            interval=FeeIntervals.MONTHLY,
            amount=10,
        )
        self.make_paid(pays_too_much, overly=True)
        will_join = Member.objects.create(
            number='6',
            name='Francine Futuremember',
            address='Future St 3\nFuture Town',
            email='francine@group.org',
        )
        Membership.objects.create(
            member=will_join,
            start=make_date(relativedelta(months=-2)),
            interval=FeeIntervals.MONTHLY,
            amount=10,
        )

    @transaction.atomic()
    def handle(self, *args, **options):
        self.create_configs()
        self.create_accounts()
        self.create_membership_types()
        self.create_members()
