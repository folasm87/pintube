#!flask/bin/python

"""
from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('yourserver.key')
context.use_certificate_file('yourserver.crt')
"""

from pintube import app
app.run(debug=True)#, ssl_context=context)