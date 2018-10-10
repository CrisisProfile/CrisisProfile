from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.conf import settings

import json
from crisisprofile.models import Profile, UserHasAccessTo

def ensure_profile_exists(user):
    profile_query = Profile.objects.filter(user=user)
    if not profile_query:
        profile = Profile(user=user, data={})
        profile.save()


def convert(data):
    if isinstance(data, bytes):
        return data.decode('ascii')
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return map(convert, data)

    return data

def get_public_uuid(user):
    return Profile.objects.get(user=user).public_uuid

@require_http_methods(['GET'])
def homepage(request):

    if request.user.is_authenticated():
        ensure_profile_exists(request.user)
        return redirect('profiles/%s' % (get_public_uuid(request.user)))
    return render(request, 'homepage.html')


def get_profile(request, public_uuid):
    data = get_profile_data(public_uuid)
    data.update({'public_uuid': public_uuid})
    return render(request, 'profile.html', data)


def get_profile_data(public_uuid):
    profile = Profile.objects.filter(public_uuid=public_uuid)[0]
    profile = profile.data
    keys_to_redact = ['identity__SSN', "identity__US_state_ID"]
    for key in keys_to_redact:
        if '__' in key:
            key_parts = key.split('__')
            if key_parts[0] in profile:
                if key_parts[1] in profile[key_parts[0]]:
                    del profile[key_parts[0]][key_parts[1]]
        else:
            if key in profile:
                del profile[key]
    return profile

def get_public_uuid(user):
    return Profile.objects.filter(user=user)[0].public_uuid

def api_get_users_have_access_to(request):
    users = [{'first_name': x.other.first_name, 'last_name': x.other.last_name, 'public_uuid': get_public_uuid(x.other)} for x in UserHasAccessTo.objects.filter(user=request.user)]
    return JsonResponse(users, safe=False)

def api_get_profile(request, public_uuid=None):
    if not public_uuid:
        public_uuid = Profile.objects.filter(user=request.user)[0].public_uuid
    profile = get_profile_data(public_uuid)
    return JsonResponse(profile, safe=False)


def api_save_thought(request):
    user = Profile.objects.filter(user=request.user)[0]
    data = user.data
    import datetime, time
    datetime_utc = datetime.datetime.utcnow()
    js_datetime = int(time.mktime(datetime_utc.timetuple())) * 1000
    new_thought = {'datetime': js_datetime, 'thought': request.POST['thought']}
    if not 'thoughts' in user.data:
        user.data['thoughts'] = []
    if 'phrases_to_ai_response' in user.data:
        for response_group in user.data['phrases_to_ai_response']:
            for phrase in response_group['phrases']:
                if phrase['phrase'].lower() in request.POST['thought'].lower():
                    new_thought['automatic_response'] = response_group['response']
    user.data['thoughts'].insert(0, new_thought)

    user.save()
    user = Profile.objects.filter(user=request.user)[0]
    return JsonResponse(user.data['thoughts'], safe=False)

def api_save_phrases_to_ai_response(request):
    user = Profile.objects.filter(user=request.user)[0]
    data = user.data
    post_data = request.POST
    new_mapping = {'phrases': json.loads(post_data['phrases']), 'response': post_data['response']}
    if not 'phrases_to_ai_response' in user.data:
        user.data['phrases_to_ai_response'] = []

    user.data['phrases_to_ai_response'].insert(0, new_mapping)

    user.save()
    user = Profile.objects.filter(user=request.user)[0]
    print user.data.keys()
    return JsonResponse(user.data['phrases_to_ai_response'], safe=False)

def api_create_checklist(request):
    user = Profile.objects.filter(user=request.user)[0]
    data = user.data
    new_item = {'name': request.POST['name'], 'items': list(json.loads(request.POST['items'])), 'triggers': list(json.loads(request.POST['triggers']))}
    if not 'checklists' in user.data:
        user.data['checklists'] = {'definitions': [new_item], 'instances': []}
    else:
        user.data['checklists']['definitions'].append(new_item)

    user.save()
    user = Profile.objects.filter(user=request.user)[0]
    return JsonResponse(user.data['checklists'], safe=False)

def update_identity(request):
    user = Profile.objects.filter(user=request.user)[0]
    data = user.data
    if not 'identity' in data:
        data['identity'] = {}
    if 'first_name' in request.POST:
        first_name = request.POST['first_name']
        data['identity']['first_name'] = first_name
    user.data = data
    user.save()
