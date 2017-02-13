from django.shortcuts import render


def get_contacts(request):
    return render(request, 'contactlist/contacts.html')
