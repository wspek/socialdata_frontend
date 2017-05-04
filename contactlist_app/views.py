from __future__ import absolute_import, unicode_literals
import os
import logging
import pdb
from celery import task
from celery.contrib import rdb
from celery.result import AsyncResult
from celery.app.task import Task
import crawler
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from .forms import AccountForm, ActionForm, ProfileForm, MutualContactsForm
from wsgiref.util import FileWrapper

# Logging
logger = logging.getLogger(__name__)

socialcrawler = crawler.Crawler()  # TODO: This has to change

task_id_global = ''


# @shared_task
@csrf_exempt
def poll_state(request):
    if request.is_ajax():
        logger.debug("--- POLL STATE ---")
        logger.debug("Session: {0}.".format(request.session.session_key))

        try:
            task_id = request.session['current_task_id']
        except:
            task_id = ""
            logger.debug("The task_id was not found in session '{0}'.".format(request.session.session_key))

        # Retrieve task belonging to the ID
        task = AsyncResult(task_id)

        logger.debug("Polling state for task: {0}".format(task_id))
        logger.debug("Task state: {0}".format(task.state))
        logger.debug("Task info: {0}".format(json.dumps(task.info)))

        progress = 0
        if task.state == "PROGRESS":
            progress = task.info["progress"]
        elif task.state == "SUCCESS":
            request.session['current_task_id'] = ""
            request.session.save()
            progress = 100
        else:
            progress = -1

        return JsonResponse({'state': task.state, 'progress': progress})
    else:
        return JsonResponse({'state': "ERROR", 'progress': -1})


def account(request):
    logger.debug("Incoming request of type: {0}.".format(request.method))

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AccountForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # social_network = form.cleaned_data['social_network']
            social_network = u"FACEBOOK"  # TODO

            request.session['username'] = username
            request.session['password'] = password
            request.session['social_network'] = social_network

            logger.debug("Entered data - user_name: {0}, password: {1}, social_network: {2}"
                         .format(username, password, social_network))

            login(username, password, social_network)

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

            username = request.session['username']
            password = request.session['password']
            social_network = request.session['social_network']
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

            logger.debug(
                "IN GETCONTACTS: {0}. {1}. {2}.".format(username, password, social_network))

            result = dispatch_get_contacts_file.delay(username, password, social_network,
                                                      profile_id, output_file_type, file_path)

            request.session.modified = True
            request.session['current_task_id'] = result.task_id
            request.session.save()

            logger.debug("Returned from 'dispatch_get_contacts_file'.")
            logger.debug("Session: {0}.".format(request.session.session_key))

            logger.debug("Current task ID: {0}".format(request.session['current_task_id']))

            path = result.get()

            logger.debug("Path is '{0}'.".format(path))

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


def update_progress(task, task_id, progress, min=0, max=100):
    # Progress of x% on a scale of 0-100% maps to a progress of mapped_progress% on a scale of min-max%
    try:
        progress_range = max - min
        mapping_multiplier = progress_range / 100.0
        mapped_progress = int(min + (progress * mapping_multiplier))

        task.update_state(task_id, state='PROGRESS', meta={'progress': mapped_progress})
    except:
        rdb.set_trace()

@task(bind=True)
def dispatch_get_contacts_file(self, username, password, social_network, profile_id, file_format, file_path):
    task_id = dispatch_get_contacts_file.request.id

    logger.debug("Dispatched task with id = '{0}'.".format(task_id))

    update_progress(self, task_id, 10)

    logger.debug("Creating crawler.")

    mycrawler = crawler.Crawler()

    logger.debug("Opening new session.")

    mycrawler.open_session(social_network, username, password)

    update_progress(self, task_id, 20)

    logger.debug("Session opened.")

    contacts_file = None
    try:
        logger.debug("Attempting to retrieve contacts from backend...")
        logger.debug("Profile ID: '{0}'.".format(profile_id))

        contacts_file = mycrawler.get_contacts_file(profile_id, file_format, file_path,
                                                    lambda p: update_progress(self, task_id, p, min=20, max=100))

        logger.debug("Contacts retrieved from backend.")
    except Exception as e:
        logger.debug("An error occurred while retrieving contacts from backend: {0}.".format(e))

        mycrawler.close_session()

    if contacts_file is not None:  # TODO contact file accessed before initialization
        logger.debug("Contacts file available: '{0}'".format(os.path.abspath(contacts_file)))
        return os.path.abspath(contacts_file)
    else:
        logger.debug("Contacts file was empty.")
        return ""


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
# def process(
