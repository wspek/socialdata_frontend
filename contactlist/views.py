from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import AccountForm


def get_contacts(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AccountForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # subject = form.cleaned_data['subject']
            # message = form.cleaned_data['message']
            # sender = form.cleaned_data['sender']
            # cc_myself = form.cleaned_data['cc_myself']
            #
            # recipients = ['info@example.com']
            # if cc_myself:
            #     recipients.append(sender)

            # send_mail(subject, message, sender, recipients)
            return HttpResponseRedirect('/contacts/profile/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AccountForm()

    return render(request, 'contactlist/contacts.html', {'form': form})