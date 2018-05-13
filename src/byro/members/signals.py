import django.dispatch

new_member_mail_information = django.dispatch.Signal()
"""
Receives the new member as signal. Response will be added to the email
welcoming the new member.
"""
new_member_office_mail_information = django.dispatch.Signal()
"""
Receives the new member as signal. Response will be added to the email
notifying the office about the new member.
"""
new_member = django.dispatch.Signal()
"""
Receives the member as signal. Response will be appended to the member edit
data form.
Parameters:
 + instantiate: Helper function to instantiate a form class with data.
"""
edit_member_form = django.dispatch.Signal()
"""
Receives the member as signal. Response should be a list of
byro.common.models.contact.Contact instances (either EMailContact or SnailMailContact).
Parameters:
 + generic_contact: Boolean, want generic contact information
 + administrative_contact: Boolean, want administrative contact information
 + billing_contact: Boolean, want billing contact information
"""
member_contacts = django.dispatch.Signal()
"""
Receives the new member as signal. If an exception is raised, the error
message will be displayed in the frontend as a warning.
"""
leave_member_mail_information = django.dispatch.Signal()
"""
Receives the leaving member as signal. Response will be added to the email
confirming termination to the member.
"""
leave_member_office_mail_information = django.dispatch.Signal()
"""
Receives the leaving member as signal. Response will be added to the email
notifying the office about the termination of the member.
"""
leave_member = django.dispatch.Signal()
"""
Receives the new member as signal. If an exception is raised, the error
message will be displayed in the frontend as a warning.
"""
