from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView

from byro.bookkeeping.models import Account, Booking, BookingType, Transaction


class NewBookingForm(forms.Form):
    memo = forms.CharField(label=_('Memo'), max_length=1000, required=False)
    member = Booking._meta.get_field('member').formfield()
    account = Booking._meta.get_field('account').formfield()
    debit_value = forms.DecimalField(min_value=0, max_digits=8, decimal_places=2, required=False)
    credit_value = forms.DecimalField(min_value=0, max_digits=8, decimal_places=2, required=False)


class TransactionDetailView(ListView):
    template_name = 'office/transaction/detail.html'
    context_object_name = 'bookings'
    model = Transaction
    paginate_by = None

    @cached_property
    def transaction_balance(self):
        o = self.get_object()
        return o.total_debit() - o.total_credit()

    def get_form(self, input_data=None):
        form = NewBookingForm(input_data)
        form.fields['account'].required = True
        form.fields['member'].required = False
        if self.transaction_balance < 0:
            form.fields['debit_value'].initial = -self.transaction_balance
        else:
            form.fields['credit_value'].initial = self.transaction_balance
        return form

    def get_object(self):
        return Transaction.objects.get(pk=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_object().bookings.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['BookingType'] = BookingType
        context['transaction'] = self.get_object()
        context['transaction_balance'] = self.transaction_balance
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST)
        t = self.get_object()
        if form.is_valid():
            arguments = dict(
                memo=form.cleaned_data['memo'],
                account=form.cleaned_data['account'],
                member=form.cleaned_data['member'],
                importer="_manual_entry",
            )
            if form.cleaned_data['debit_value']:
                t.debit(amount=form.cleaned_data['debit_value'], **arguments)
            if form.cleaned_data['credit_value']:
                t.credit(amount=form.cleaned_data['credit_value'], **arguments)
            t.save()
            messages.success(self.request, _('The transaction was updated.'))

        if t.is_balanced():
            if 'in_account' in request.GET:
                account = Account.objects.get(pk=request.GET['in_account'])
                if account.unbalanced_transactions.count():
                    return redirect(
                        "{}?filter=unbalanced".format(
                            reverse('office:finance.accounts.detail', kwargs={'pk': account.pk})
                        )
                    )
            return redirect('office:finance.accounts.list')
        if 'in_account' in request.GET:
            return redirect(
                "{}?in_account={}".format(
                    reverse('office:finance.transactions.detail', kwargs={'pk': t.pk}),
                    request.GET['in_account']
                )
            )
        else:
            return redirect("office:finance.transactions.detail", pk=t.pk)
