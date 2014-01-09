#!/usr/bin/python

import gdata.youtube
import cgi
import cgitb; cgitb.enable()

parameters = cgi.FieldStorage()
authsub_token = parameters['token']

print "content-type:text/html\n"

#debugging
print authsub_token

gd_client = gdata.photos.service.PhotosService()
gd_client.auth_token = authsub_token
gd_client.UpgradeToSessionToken()

#more debugging
print "BLINKENLICHTEN"