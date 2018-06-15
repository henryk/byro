import django

process_transaction = django.dispatch.Signal(providing_args=[])

process_csv_upload = django.dispatch.Signal(providing_args=[])
"""
This signal provides a RealTransactionSource as sender and expects a list of
one or more RealTransactions in response.

If the RealTransactionSource has already been processed, no RealTransactions
should be created, unless you are very sure what you are doing.
"""
