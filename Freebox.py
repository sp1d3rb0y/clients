## Freebox.py for Freebox API in freebox-client
##
## Made by spiderboy
## Spiderboy   <spiderboy@spiderboy.fr>
##
## Started on  Sat Aug  9 02:38:27 2014 spiderboy
## Last update Mon Aug 11 20:49:09 2014 spiderboy
##
#!/usr/bin/python

import requests
import socket
import cPickle as pickle
import os.path
import json
import time
from hashlib import sha1
import hmac

# TODO : first run
# Requests an app_token, store it securely with cPicle

class Freebox:
    def __init__(self):
        self._appinfos = {
            "app_id" : "fr.freebox.pyclient",
            "app_name" : "Freebox Python Client",
            "app_version" : "0.1",
            "device_name" : "",
        }
        self._baseurl = "http://mafreebox.freebox.fr"
        self._baseurl += self._build_url_for_api_version()
        self._appinfos["device_name"] = socket.gethostname()
        self._tokenfile = "token.p"
        self._app_token = self._get_app_token()
        self._session_token = ""
        self._authenticated = False

    def _build_url_for_api_version(self):
        uri = "api_version"
        req = requests.get(self._baseurl + "/" + uri)
        assert req.status_code == 200
        version_result = req.json
        self._api_version = version_result[uri]
        if version_result["api_base_url"].startswith("/"):
            start = version_result["api_base_url"]
        else:
            start = "/" + version_result["api_base_url"]
        if not version_result["api_base_url"].endswith("/"):
            start += "/"
        major = self._api_version.split('.')[0]
        return "%sv%s" % (start, major)

    def _make_request(self, url):
        headers = {"X-Fbx-App-Auth" : self._session_token}
        req = requests.get(url, headers = headers)
        if req.status_code == 403:
            self._authenticated = False
            return None
        assert req.status_code == 200
        res = req.json
        assert res["success"] is True
        return res["result"]

    def _get_app_token(self):
        if os.path.isfile(self._tokenfile):
            tok = pickle.load(open(self._tokenfile, "rb"))
            self._app_token = tok.encode('ascii','ignore')
            return tok.encode('ascii','ignore')
        else:
            return None

    def _set_app_token(self, token):
        pickle.dump(token, open(self._tokenfile, "wb"))
        self._app_token = token

    def _get_session_token(self):
        # Get challenge
        url = self._baseurl + "/login/"
        res = self._make_request(url)
        challenge = res["challenge"].encode('ascii','ignore')
        password = hmac.new(self._app_token, challenge, sha1)
        data = {
            "app_id" : self._appinfos["app_id"],
            "password" : password.hexdigest()
        }
        url += "session/"
        req = requests.post(url, data = json.dumps(data))
        assert req.status_code == 200
        res = req.json
        assert res["success"] is True
        return res["result"]["session_token"]

    def login(self):
        if self._app_token is None:
            # First run, request a unique token for this app
            url = self._baseurl + "/login/authorize/"
            req = requests.post(url, data = json.dumps(self._appinfos))
            assert req.status_code == 200
            res = req.json
            assert res["success"] is True
            tok = res["result"]["app_token"]
            track_id = res["result"]["track_id"]
            # Wait for authorization by user on Box
            url += str(track_id)
            for i in range(20):
                res = self._make_request(url)
                if res["status"] == "granted":
                    break
                time.sleep(1)
            if res["status"] == "granted":
                self._set_app_token(tok.encode('ascii', 'ignore'))
            else:
                # User did not validate application in time
                raise Exception("User did not authorize application in time.")

        if not self._authenticated:
            self._session_token = self._get_session_token()
            self._authenticated = True

    def logout(self):
        headers = {"X-Fbx-App-Auth" : self._session_token}
        url = self._baseurl + "/login/logout/"
        req = requests.post(url, headers = headers)
        assert req.status_code == 200
        res = req.json
        assert res["success"] is True
        self._authenticated = False
        self._session_token = ""

    # IN KB/s
    # bandwidth_up : Max up bandwith
    # bandwidth_down : Max down bandwith
    # rate_up : Current up bandwith
    # rate_down : Current down bandwith
    def get_connection(self):
        if not self._authenticated:
            self.login()
        url = self._baseurl + "/connection/"
        res = self._make_request(url)
        return res
