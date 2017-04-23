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
            output_file_type = form.cleaned_data['output_file_type']

            if output_file_type == "EXCEL":
                file_format = crawler.FileFormat.EXCEL
                file_path = './contacts.xlsx'
                content_type = ''
            elif output_file_type == "CSV":
                file_format = crawler.FileFormat.CSV
                file_path = './contacts.csv'
                content_type = 'text/csv'

            path = process(profile_id, file_format, file_path)
            wrapper = FileWrapper(file(path))
            response = HttpResponse(wrapper, content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename={0}'.format(file_path[2:])
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
            output_file_type = form.cleaned_data['output_file_type']

            logger.debug(
                "Attempting to retrieve mutual contacts between '{0}' and '{1}'.".format(profile_id1, profile_id2))

            if output_file_type == "EXCEL":
                file_format = crawler.FileFormat.EXCEL
                file_path = './mutual_contacts.xlsx'
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif output_file_type == "CSV":
                file_format = crawler.FileFormat.CSV
                file_path = './mutual_contacts.csv'
                content_type = 'text/csv'

            contacts_file = socialcrawler.get_mutual_contacts_file(profile_id1, profile_id2, file_format, file_path)

            if contacts_file is not None:
                logger.debug("Contacts file available: '{0}'".format(os.path.abspath(contacts_file)))
                path = os.path.abspath(contacts_file)
            else:
                path = ""

            wrapper = FileWrapper(file(path))
            response = HttpResponse(wrapper, content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename={0}'.format(file_path[2:])
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


# TODO: Does the function really need to be separate? In that case rename it.
def process(profile_id, file_format, file_path):
    contacts_file = None

    try:
        logger.debug("Attempting to retrieve contacts from backend...")
        logger.debug("Profile ID: '{0}'.".format(profile_id))
        # contacts_file = socialcrawler.get_contacts_file(profile_id, crawler.FileFormat.CSV,
        #                                                 "./contacts_{0}.csv".format(profile_id))
        contacts_file = socialcrawler.get_contacts_file(profile_id, file_format, file_path)
        # contacts_file = socialcrawler.get_contacts_file(profile_id, crawler.FileFormat.CSV, './contacts.csv')
        logger.debug("Contacts retrieved from backend.")
    except Exception as e:
        logger.debug("An error occurred while retrieving contacts from backend: {0}.".format(e))

    socialcrawler.close_session()

    if contacts_file is not None:  # TODO contact file accessed before initialization
        logger.debug("Contacts file available: '{0}'".format(os.path.abspath(contacts_file)))
        return os.path.abspath(contacts_file)
    else:
        logger.debug("Contacts file was empty.")
        return ""
