import os
import logging
import pdb

import crawler
from django.http import HttpResponseRedirect, HttpResponse
from wsgiref.util import FileWrapper
from django.shortcuts import render
from .forms import AccountForm, ActionForm, ProfileForm, MutualContactsForm

# Logging
logger = logging.getLogger(__name__)

socialcrawler = crawler.Crawler()  # TODO: This has to change


def account(request):
    logger.debug("Incoming request of type: {0}.".format(request.method))

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AccountForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            user_name = form.cleaned_data['user_name']
            password = form.cleaned_data['password']
            # social_network = form.cleaned_data['social_network']
            social_network = u"FACEBOOK"  # TODO

            logger.debug("Entered data - user_name: {0}, password: {1}, social_network: {2}"
                         .format(user_name, password, social_network))

            login(user_name, password, social_network)

            logger.debug("Login process finished. Might be logged in or not.")

            return HttpResponseRedirect('/contacts/action/')
            # return HttpResponseRedirect('/contacts/profile/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = AccountForm()

    return render(request, 'contactlist_app/account.html', {'form': form})


def action(request):
    logger.debug("Incoming request of type: {0}.".format(request.method))

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ActionForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            if 'profile' in request.POST:
                return HttpResponseRedirect('/contacts/profile/')
            elif 'mutuals' in request.POST:
                return HttpResponseRedirect('/contacts/mutuals/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ActionForm()

    return render(request, 'contactlist_app/action.html', {'form': form})


def get_contacts(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        logger.debug("Attempting to get contacts.")

        # create a form instance and populate it with data from the request:
        form = ProfileForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            logger.debug("Checking validity of form.")

            profile_id = form.cleaned_data['profile_id']
            path = process(profile_id)
            wrapper = FileWrapper(file(path))
            response = HttpResponse(wrapper, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=contacts.csv'
            response['Content-Length'] = os.path.getsize(path)

            logger.debug("Returning response, in the form of a file wrapper.")

            return response
    # if a GET (or any other method) we'll create a blank form
    else:
        logger.debug("Contacts page entered.")
        form = ProfileForm()

    return render(request, 'contactlist_app/profile.html', {'form': form})


def get_mutual_contacts(request):
    logger.debug("Incoming request of type: {0}.".format(request.method))

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = MutualContactsForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            logger.debug("Checking validity of form.")

            profile_id1 = form.cleaned_data['profile_id1']
            profile_id2 = form.cleaned_data['profile_id2']

            logger.debug(
                "Attempting to retrieve mutual contacts between '{0}' and '{1}'.".format(profile_id1, profile_id2))

            contacts_file = socialcrawler.get_mutual_contacts_file(profile_id1, profile_id2, crawler.FileFormat.CSV)

            if contacts_file is not None:
                logger.debug("Contacts file available: '{0}'".format(os.path.abspath(contacts_file)))
                path = os.path.abspath(contacts_file)
            else:
                path = ""

            wrapper = FileWrapper(file(path))
            response = HttpResponse(wrapper, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=mutual_contacts.csv'
            response['Content-Length'] = os.path.getsize(path)

            logger.debug("Returning response, in the form of a file wrapper.")

            return response
    # if a GET (or any other method) we'll create a blank form
    else:
        form = MutualContactsForm()

    return render(request, 'contactlist_app/mutuals.html', {'form': form})


def download(request):
    return render(request, 'contactlist_app/download.html')


def login(username, password, medium):
    network = None
    if medium == "FACEBOOK":
        network = crawler.SocialMedia.FACEBOOK
    elif medium == "LINKEDIN":
        network = crawler.SocialMedia.LINKEDIN

    # TODO: Data validation?

    socialcrawler.open_session(network, username, password)
    # logger.debug("Exception occurred while logging in.")


def process(profile_id):
    contacts_file = None

    try:
        logger.debug("Attempting to retrieve contacts from backend...")
        logger.debug("Profile ID: '{0}'.".format(profile_id))
        # contacts_file = socialcrawler.get_contacts_file(profile_id, crawler.FileFormat.CSV,
        #                                                 "./contacts_{0}.csv".format(profile_id))
        contacts_file = socialcrawler.get_contacts_file(profile_id, crawler.FileFormat.CSV)
        logger.debug("Contacts retrieved from backend.")
    except Exception as e:
        logger.debug("An error occurred while retrieving contacts from backend.")

    socialcrawler.close_session()

    if contacts_file is not None:   #TODO contact file accessed before initialization
        logger.debug("Contacts file available: '{0}'".format(os.path.abspath(contacts_file)))
        return os.path.abspath(contacts_file)
    else:
        logger.debug("Contacts file was empty.")
        return ""
