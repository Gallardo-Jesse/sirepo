# -*- coding: utf-8 -*-
u"""Import a single archive

:copyright: Copyright (c) 2017 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function
from pykern.pkdebug import pkdp


def do_form(form):
    """Self-extracting archive post

    Args:
        form (flask.request.Form): what to import

    Returns:
        dict: data
    """
    from sirepo import cookie
    from sirepo import uri_router
    from sirepo import simulation_db
    import base64
    import StringIO

    if not 'zip' in form:
        raise uri_router.NotFound('missing zip in form')
    data = read_zip(StringIO.StringIO(base64.decodestring(form['zip'])))
    data.models.simulation.folder = '/Import'
    data.models.simulation.isExample = False
    return simulation_db.save_new_simulation(data)


def read_json(text, sim_type=None):
    """Read json file and return

    Args:
        text (IO): file to be read
        sim_type (str): expected type

    Returns:
        dict: data
    """
    from sirepo import simulation_db

    # attempt to decode the input as json first, if invalid try python
    # fixup data in case new structures are need for lib_files() below
    data = simulation_db.fixup_old_data(simulation_db.json_load(text))[0]
    if sim_type:
        assert data.simulationType == sim_type, \
            'simulationType={} invalid, expecting={}'.format(
                data.simulationType,
                sim_type,
            )
    return data


def read_zip(stream, sim_type=None):
    """Read zip file and store contents

    Args:
        stream (IO): file to read
        sim_type (module): expected app

    Returns:
        dict: data
    """
    from pykern import pkcollections
    from sirepo import simulation_db
    from sirepo.template import template_common
    import py.path
    import re
    import zipfile

    tmp = simulation_db.tmp_dir()
    data = None
    zipped = pkcollections.Dict()
    with zipfile.ZipFile(stream, 'r') as z:
        for i in z.infolist():
            b = py.path.local(i.filename).basename
            c = z.read(i)
            if b.lower() == simulation_db.SIMULATION_DATA_FILE:
                assert not data, \
                    'too many db files {} in archive'.format(b)
                data = read_json(c, sim_type)
                continue
            if '__MACOSX' in i.filename:
                continue
            #TODO(robnagler) ignore identical files hash
            assert not b in zipped, \
                '{} duplicate file in archive'.format(i.filename)
            zipped[b] = tmp.join(b)
            zipped[b].write(c, 'wb')
    assert data, \
        'missing {} in archive'.format(simulation_db.SIMULATION_DATA_FILE)
    needed = pkcollections.Dict()
    for n in template_common.lib_files(data):
        assert n.basename in zipped or n.check(file=True, exists=True), \
            'auxiliary file {} missing in archive'.format(n.basename)
        needed[n.basename] = n
    lib_d = simulation_db.simulation_lib_dir(data.simulationType)
    for b, src in zipped.items():
        if b in needed:
            src.copy(needed[b])
    return data
