# -*- coding: utf-8 -*-
"""Runs the server in uwsgi or http modes

:copyright: Copyright (c) 2015 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function

import os
import subprocess
import sys

import py

from pykern.pkdebug import pkdc, pkdp
from pykern import pkcli
from pykern import pkinspect
from pykern import pkio
from pykern import pkjinja

_DEFAULT_PORT = 8000
_DEFAULT_SUBDIR = 'run'


def http(port=None, run_dir=None):
    """Starts Flask server"""
    from sirepo import server
    server.init(_run_dir(run_dir))
    server.app.run(host='0.0.0.0', port=_port(port), debug=1)


def uwsgi(port=None, run_dir=None, daemon=False):
    run_dir =_run_dir(run_dir)
    values = {
        'run_dir': run_dir,
        'port': _port(port),
        'daemon': daemon,
    }
    # uwsgi.py must be first, because referenced by uwsgi.yml
    for f in ('uwsgi.py', 'uwsgi.yml'):
        output = run_dir.join(f)
        values[f.replace('.', '_')] = str(output)
        pkjinja.render_resource(f, values, output=output)
    subprocess.check_call(['uwsgi', '--yaml=' + values['uwsgi_yml']])


def _port(port):
    """Returns port or default"""
    try:
        if port:
            res = int(port)
            # http://stackoverflow.com/a/924337
            if res <= 5000 or res >= 32768:
                pkcli.command_error('{}: port is outside 5001 .. 32767', port)
            return res
    except ValueError:
        pkcli.command_error('{}: port is not an int', port)
    return _DEFAULT_PORT


def _run_dir(run_dir):
    """Returns root package's parent or cwd with _DEFAULT_SUBDIR"""
    if not run_dir:
        fn = sys.modules[pkinspect.root_package(http)].__file__
        root = py.path.local(py.path.local(py.path.local(fn).dirname).dirname)
        # Check to see if we are in our dev directory. This is a hack,
        # but should be reliable.
        if not root.join('requirements.txt').check():
            # Don't run from an install directory
            root = py.path.local('.')
        run_dir = root.join(_DEFAULT_SUBDIR)
    pkdp(run_dir)
    return pkio.mkdir_parent(run_dir)
