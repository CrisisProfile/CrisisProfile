import requests
from social_core.backends.oauth import BaseOAuth2
import json
import settings

class Auth0(BaseOAuth2):
    """Auth0 OAuth authentication backend"""
    name = 'auth0'
    SCOPE_SEPARATOR = ' '
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ("last_ip", "last_ip"),
        ("updated_at", "updated_at"),
        ("identities", "identities"),
        ("relationToViewer", "relationToViewer"),
        ("user_id", "user_id"),
        ("headline", "headline"),
        ("siteStandardProfileRequest", "siteStandardProfileRequest"),
        ("pictureUrls", "pictureUrls"),
        ("last_login", "last_login"),
        ("given_name", "given_name"),
        ("email", "email"),
        ("location", "location"),
        ("picture", "picture"),
        ("distance", "distance"),
        ("apiStandardProfileRequest", "apiStandardProfileRequest"),
        ("publicProfileUrl", "publicProfileUrl"),
        ("nickname", "nickname"),
        ("name", "name"),
        ("family_name", "family_name"),
        ("numConnections", "numConnections"),
        ("positions", "positions"),
        ("industry", "industry"),
        ("email_verified", "email_verified"),
        ("numConnectionsCapped", "numConnectionsCapped"),
        ("created_at", "created_at"),
        ("logins_count", "logins_count"),
    ]
    print "auth0 class"

    def authorization_url(self):
        """Return the authorization endpoint."""
        print 'auth url'
        return "https://" + self.setting('DOMAIN') + "/authorize"

    def access_token_url(self):
        """Return the token endpoint."""
        print 'auth token'
        return "https://" + self.setting('DOMAIN') + "/oauth/token"

    def get_user_id(self, details, response):
        """Return current user id."""
        print 'user id'
        return details['user_id']

    def get_management_api_token(self):

        payload = "{\"grant_type\":\"client_credentials\",\"client_id\": \"%s\",\"client_secret\": \"%s\",\"audience\": \"https://cisisprofile.auth0.com/api/v2/\"}" % (settings.AUTH0_MANAGEMENT_KEY, settings.AUTH0_MANAGEMENT_SECRET)

        headers = { 'content-type': "application/json" }

        response = requests.post("https://"+self.setting("SOCIAL_AUTH_AUTH0_KEY")+"/oauth/token", data=payload, headers=headers)
        print response.text


        return response.json()['access_token']

    def get_user_details(self, response):
        url = 'https://' + self.setting('DOMAIN') + '/userinfo'
        print url
        headers = {'authorization': 'Bearer ' + response['access_token']}
        print 'headers', headers
        resp = requests.get(url, headers=headers)
        userinfo = resp.json()
        token = self.get_management_api_token()
        headers = {'authorization': 'Bearer ' + token}

        url = 'https://' + self.setting('DOMAIN') + userinfo['sub']
        resp = requests.get(url, headers=headers)
        print 'all', resp.json().keys()
        print 'userinfo', userinfo

        d = {'username': userinfo['nickname'],
                'first_name': userinfo.get('given_name'),
                'picture': userinfo.get('picture'),
                'user_id': userinfo.get('sub')}
        d.update(resp.json())
        return d
