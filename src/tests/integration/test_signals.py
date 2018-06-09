import pytest

from byro.bookkeeping.models import Account, AccountCategory
from byro.members.models import Member


class connected_signal:
    """ connect a signal and make sure it is disconnected after use, so it doesn't leak into other tests. """

    def __init__(self, signal, receiver):
        self.signal = signal
        self.receiver = receiver

    def __enter__(self):
        self.signal.receivers = []
        self.signal.connect(self.receiver, dispatch_uid='test-plugin')

    def __exit__(self, exc_type, exc_value, tb):
        self.signal.disconnect(self.receiver, dispatch_uid='test-plugin')
