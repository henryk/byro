from django.db import models

from byro.common.models.auditable import Auditable
from byro.common.models.choices import Choices


class SourceState(Choices):
    NEW = 'new'
    PROCESSING = 'processing'
    PROCESSED = 'processed'
    FAILED = 'failed'


class RealTransactionSource(Auditable, models.Model):
    source_file = models.FileField(upload_to='transaction_uploads/')
    state = models.CharField(default=SourceState.NEW, choices=SourceState.choices, max_length=SourceState.max_length)
