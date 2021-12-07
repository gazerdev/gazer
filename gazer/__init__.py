from flask import Flask
import os
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

from gazer import views

def startup():
    '''Handle any application startup tasks'''
    if not os.path.isfile('postdata.db'):
        import gazer.create_data
    if not os.path.isdir('dd_pretrained'):
        print('dd not enabled')

startup()