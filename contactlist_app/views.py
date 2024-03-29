from __future__ import absolute_import, unicode_literals
import os
import logging
from celery import task
from celery.result import AsyncResult
import crawler
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from .forms import AccountForm, ActionForm, ProfileForm, MutualContactsForm
from wsgiref.util import FileWrapper

# Logging
logger = logging.getLogger(__name__)


def account(request):
    logger.info("Incoming request: {0} {1}".format(request.method, request.path))

    request.session.set_test_cookie()

    logger.info("Cookie set.")

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
            request.session.modified = True

            logger.info("Entered data - user_name: {0}, password: {1}, social_network: {2}"
                        .format(username, password, social_network))

            return HttpResponseRedirect('/contacts/action/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = AccountForm()

    return render(request, 'contactlist_app/account.html', {'form': form})


def action(request):
    logger.info("Incoming request: {0} {1}".format(request.method, request.path))

    logger.info("Cookie:")

    if request.session.test_cookie_worked():
        logger.info("*** TRUE ***")
    else:
        logger.info("*** FALSE ***")

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
    logger.info("Incoming request: {0} {1}".format(request.method, request.path))

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
                file_path = './contacts.xlsx'
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif output_file_type == "CSV":
                file_path = './contacts.csv'
                content_type = 'text/csv'

            logger.info(
                "Attempting to retrieve contacts for '{0}'.".format(profile_id))

            logger.debug(
                "dispatch_get_contacts_file({0}, {1}, {2}, {3}, {4}, {5})".format(username, password, social_network,
                                                                                  profile_id, output_file_type,
                                                                                  file_path))

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

            logger.info("Returning response, in the form of a file wrapper.")

            return response
    # if a GET (or any other method) we'll create a blank form
    else:
        logger.debug("Contacts page entered.")
        form = ProfileForm()

    return render(request, 'contactlist_app/profile.html', {'form': form})


@task(bind=True)
def dispatch_get_contacts_file(self, username, password, social_network, profile_id, file_format, file_path):
    task_id = dispatch_get_contacts_file.request.id

    logger.info("Dispatched task with id = '{0}'.".format(task_id))

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
                                                    lambda p: update_progress(self, task_id, p, min_value=20,
                                                                              max_value=100))

        logger.debug("Contacts retrieved from backend.")
    except Exception as e:
        logger.warning("An error occurred while retrieving contacts from backend: {0}.".format(e))

        mycrawler.close_session()

    if contacts_file is not None:  # TODO contact file accessed before initialization
        logger.info("Contacts file available: '{0}'".format(os.path.abspath(contacts_file)))
        return os.path.abspath(contacts_file)
    else:
        logger.debug("Contacts file was empty.")
        return ""


def get_mutual_contacts(request):
    logger.info("Incoming request: {0} {1}".format(request.method, request.path))

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        logger.debug("Attempting to get mutual contacts.")

        # create a form instance and populate it with data from the request:
        form = MutualContactsForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            logger.debug("Checking validity of form.")

            username = request.session['username']
            password = request.session['password']
            social_network = request.session['social_network']
            profile_id1 = form.cleaned_data['profile_id1']
            profile_id2 = form.cleaned_data['profile_id2']
            output_file_type = form.cleaned_data['output_file_type']

            if output_file_type == "EXCEL":
                file_path = './mutual_contacts.xlsx'
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif output_file_type == "CSV":
                file_path = './mutual_contacts.csv'
                content_type = 'text/csv'

            logger.info(
                "Attempting to retrieve mutual contacts between '{0}' and '{1}'.".format(profile_id1, profile_id2))

            # DISPATCH
            result = dispatch_get_mutual_contacts_file.delay(username, password, social_network,
                                                             profile_id1, profile_id2, output_file_type, file_path)

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

            logger.info("Returning response, in the form of a file wrapper.")

            return response
    # if a GET (or any other method) we'll create a blank form
    else:
        logger.info("Mutual contacts page entered.")
        form = MutualContactsForm()

    return render(request, 'contactlist_app/mutuals.html', {'form': form})


@task(bind=True)
def dispatch_get_mutual_contacts_file(self, username, password, social_network, profile_id1, profile_id2, file_format,
                                      file_path):
    task_id = dispatch_get_mutual_contacts_file.request.id  # TODO: Should this not just be self.request.id?

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
        logger.debug("Attempting to retrieve mutual contacts from backend...")
        logger.debug("Profile ID1: '{0}' versus Profile ID2: {1}.".format(profile_id1, profile_id2))

        contacts_file = mycrawler.get_mutual_contacts_file(profile_id1, profile_id2, file_format, file_path,
                                                           lambda p: update_progress(self, task_id, p, min_value=20,
                                                                                     max_value=100))

        logger.debug("Contacts retrieved from backend.")
    except Exception as e:
        logger.warning("An error occurred while retrieving contacts from backend: {0}.".format(e))
        mycrawler.close_session()

    if contacts_file is not None:  # TODO contact file accessed before initialization
        logger.info("Mutual contacts file available: '{0}'".format(os.path.abspath(contacts_file)))
        return os.path.abspath(contacts_file)
    else:
        logger.info("Mutual contacts file was empty.")
        return ""


def download(request):
    return render(request, 'contactlist_app/download.html')


def update_progress(running_task, task_id, progress, min_value=0, max_value=100):
    # Progress of x% on a scale of 0-100% maps to a progress of mapped_progress% on a scale of min-max%
    progress_range = max_value - min_value
    mapping_multiplier = progress_range / 100.0
    mapped_progress = int(min_value + (progress * mapping_multiplier))

    running_task.update_state(task_id, state='PROGRESS', meta={'progress': mapped_progress})


@csrf_exempt
def poll_state(request):
    if request.is_ajax():
        # logger.debug("--- POLL STATE ---")
        # logger.debug("Session: {0}.".format(request.session.session_key))

        try:
            task_id = request.session['current_task_id']
        except:
            task_id = ""
            logger.warning("The task_id was not found in session '{0}'.".format(request.session.session_key))

        # Retrieve task belonging to the ID
        celery_task = AsyncResult(task_id)

        # logger.debug("Polling state for task: {0}".format(task_id))
        # logger.debug("Task state: {0}".format(celery_task.state))
        # logger.debug("Task info: {0}".format(json.dumps(celery_task.info)))

        if celery_task.state == "PROGRESS":
            progress = celery_task.info["progress"]
        elif celery_task.state == "SUCCESS":
            request.session['current_task_id'] = ""
            request.session.save()
            progress = 100
        else:
            progress = -1

        return JsonResponse({'state': celery_task.state, 'progress': progress})
    else:
        return JsonResponse({'state': "ERROR", 'progress': -1})
