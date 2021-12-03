from flask import Flask
import os
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

import views

def startup():
    '''Handle any application startup tasks'''
    if not os.path.isfile('postdata.db'):
        import create_data
    if not os.path.isdir('dd_pretrained'):
        print('dd not enabled')

if __name__ == "__main__":
    startup()
    app.run("0.0.0.0", debug=False, threaded=True)