#!/usr/bin/env python3
# 
# Heavily inspired by the code from the nextcloud-API repo
# 

# import statements
import getpass
import os
import random
import string
from unittest import TestCase
from nextcloud import NextCloud
from nextcloud.api_wrappers import WebDAV

# global nextcloud-related variables
try:
    NEXTCLOUD_URL = "https://{}".format(os.environ.get('NEXTCLOUD_HOSTNAME', 'localhost'))
except KeyError:
    print("ERR -- Nextcloud hostname was not found!")

# DO NOT HARD_CODE PASSWORDS IN PLAINTEXT! -- VC
user_username = input("Enter your username: ")
user_password = getpass.getpass("Enter your password: ")

nxc_obj = NextCloud(NEXTCLOUD_URL, user_username, user_password, json_output=True)
print(nxc_obj)

# functions
def nextcloud_api_integration_test(file_name, file_content=None, timestamp=None):
    # In order to upload the file, create it right here and now!
    # TODO replace with a `tempfile` invocation,
    # in order to prevent overwriting a local file.
    if (file_content is None):
        f = open(file_name, "r")
    else:
        f = open(file_name, "w")
        f.write(str(file_content))
    f.close()
    
    file_local_path = os.path.abspath(file_name)
    print("About to try to upload \"%s\" to %s" % (file_content, file_name))
    try:
        nxc_obj.upload_file(user_username, file_local_path, file_name, timestamp)
    except Error:
        print("Upload encountered a failure!!")
    print("Just tried to upload...")
    
    # check status code -- TODO port this functionality somehow?
    #assert res.is_ok
    #assert res.raw.status_code == self.CREATED_CODE
    
    # test uploaded file can be found with list_folders
    remote_file_location_suffix = os.path.join("/"+user_username, file_name)
    file_nextcloud_href = "/nextcloud"+WebDAV.API_URL+remote_file_location_suffix

    # TODO find out: why does this method not work?
    #file_nextcloud_href = os.path.join(WebDAV.API_URL, remote_file_location_suffix)
    folder_info = nxc_obj.list_folders(user_username, path=file_name)
    assert folder_info.is_ok
    assert len(folder_info.data) == 1
    assert isinstance(folder_info.data[0], dict)
    
    # check href
    #print("")
    #print(folder_info.data[0])
    #print("[DEBUG]    That object, which appears to be a response code, has a HREF value that needs to match: %s" % file_nextcloud_href)
    #print("[     ]    ...but does it?")
    #print("")
    assert folder_info.data[0]["href"] == file_nextcloud_href
    
    # remove file on local machine
    os.remove(file_local_path)
    nxc_obj.download_file(user_username, file_name)
    
    # test file is downloaded to current dir
    assert file_name in os.listdir(".")
    f = open(file_local_path)
    downloaded_file_content = f.read()
    assert downloaded_file_content == str(file_content)
    f.close()
    
    # delete file
    nxc_obj.delete_path(user_username, file_name)
    os.remove(file_local_path)

nextcloud_api_integration_test("content.txt", random.getrandbits(8))
