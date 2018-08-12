from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.conf import settings

import json
from crisisprofile.models import Profile

def convert(data):
    if isinstance(data, bytes):
        return data.decode('ascii')
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return map(convert, data)

    return data


@require_http_methods(['GET'])
def homepage(request):
    return render(request, 'homepage.html')

def get_profile(request, public_uuid):
    return render(request, 'profile.html', get_profile_data(public_uuid))

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

def api_get_profile(request, public_uuid):
    profile = get_profile_data(public_uuid)
    return JsonResponse(profile, safe=False)
