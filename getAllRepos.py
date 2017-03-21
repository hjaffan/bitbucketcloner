#!/usr/bin/python

import urllib2, base64, json
import sys, os
import getpass
import re
from git import Repo
p=str("null")
pas=str("password")

class PreemptiveBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
    '''Preemptive basic auth.

    Instead of waiting for a 403 to then retry with the credentials,
    send the credentials if the url is handled by the password manager.
    Note: please use realm=None when calling add_password.'''
    def http_request(self, req):
        url = req.get_full_url()
        realm = None
        # this is very similar to the code from retry_http_basic_auth()
        # but returns a request object.
        user, pw = self.passwd.find_user_password(realm, url)
        if pw:
            raw = "%s:%s" % (user, pw)
            auth = 'Basic %s' % base64.b64encode(raw).strip()
            req.add_unredirected_header(self.auth_header, auth)
        return req

    https_request = http_request

def main(argv):
    try:
        username=raw_input("Type Username: ")
        p=getpass.getpass("Type password: ")
        key=raw_input("Type project name ")
        response = callAPI(username,p,key)
        repoList = getRepoByProtocal(response)
        cloneRepos(repoList)
    except ValueError as e:
        print(e)

def getRepoByProtocal(jsonobject):
    final_list = list()
    for item in jsonobject['values']:
        for link in item['links']['clone']:
            if link['name'] == "http":
                final_list.append(link['href'])
    return final_list

def cloneRepos(repolist):
    regex = r"^(?:.*\/)*(.*)\.git$"
    current = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    cwd = os.getcwd()
    for url in repolist:
        stringtoparse = url
        folder = re.findall(regex, stringtoparse)
        path_to_clone = os.path.join(cwd, folder[0])
        print path_to_clone
        Repo.clone_from(stringtoparse,to_path=path_to_clone ,env={'GIT_SSL_NO_VERIFY': '1'})

def callAPI(username, password, key):
    url="https://api.bitbucket.org/2.0/repositories"+key
    auth_handler = PreemptiveBasicAuthHandler()
    auth_handler.add_password(
        realm=None, # default realm.
        uri=url,
        user=username,
        passwd=password)
    opener = urllib2.build_opener(auth_handler)
    response = opener.open(url)
    return json.load(response)


if __name__ == "__main__":
    main(sys.argv[1:])
