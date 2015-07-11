#!/usr/bin/env python

import os
from app import create_app
from flask.ext.script import Manager, Server
from flask import redirect, url_for


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
manager.add_command("runserver", Server(host="0.0.0.0", use_reloader=True))


@app.route('/')
def index():
    return redirect(url_for('servers'))


if __name__ == '__main__':
    manager.run()
