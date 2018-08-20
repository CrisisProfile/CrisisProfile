from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.conf import settings

import json
from crisisprofile.models import Profile, UserHasAccessTo

def ensure_profile_exists(user):
    profile_query = Profile.objects.filter(user=user)
    print(profile_query)
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

def api_get_profile(request, public_uuid):
    profile = get_profile_data(public_uuid)
    return JsonResponse(profile, safe=False)

def api_create_checklist(request):
    user = Profile.objects.filter(user=request.user)[0]
    data = user.data
    print request.POST
    new_item = {'name': request.POST['name'], 'items': request.POST['items[]']}
    if not 'checklists' in user.data:
        user.data['checkists'] = {'definitions': [new_item], 'instances': []}
    else:
        user.data['checklists'].append(new_item)
    user.save()
    user = Profile.objects.filter(user=request.user)[0]

    return JsonResponse(user.data['checklists'], safe=False)
