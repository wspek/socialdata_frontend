import os
import sys

sys.path.append('/media/waldo/DATA-SHARE/Code/SocialCrawler/src')
import pdb;

import crawler
from django.http import HttpResponseRedirect, HttpResponse
from wsgiref.util import FileWrapper
from django.shortcuts import render

from .forms import AccountForm, ProfileForm

socialcrawler = crawler.Crawler()  # TODO: This has to change


def account(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AccountForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            user_name = form.cleaned_data['user_name']
            password = form.cleaned_data['password']
            # social_network = form.cleaned_data['social_network']
            social_network = u"FACEBOOK"

            login(user_name, password, social_network)

            return HttpResponseRedirect('/contacts/profile/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = AccountForm()

    return render(request, 'contactlist/account.html', {'form': form})


def get_contacts(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProfileForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            profile_id = form.cleaned_data['profile_id']
            path = process(profile_id)
            wrapper = FileWrapper(file(path))
            response = HttpResponse(wrapper, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=contacts.csv'
            response['Content-Length'] = os.path.getsize(path)
            return response
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProfileForm()

    return render(request, 'contactlist/profile.html', {'form': form})


def download(request):
    return render(request, 'contactlist/download.html')


def login(username, password, medium):
    network = None
    if medium == "FACEBOOK":
        network = crawler.SocialMedia.FACEBOOK
    elif medium == "LINKEDIN":
        network = crawler.SocialMedia.LINKEDIN

    # TODO: Data validation?

    socialcrawler.open_session(network, username, password)


def process(profile_id):
    contacts_file = socialcrawler.get_contacts_file(profile_id, crawler.FileFormat.CSV)

    socialcrawler.close_session()

    if contacts_file is not None:
        return os.path.abspath(contacts_file)
    else:
        return ""
