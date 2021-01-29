# -*- coding: utf-8 -*-
"""Wrapper to run FLASH from the command line.

:copyright: Copyright (c) 2018 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function
from pykern import pkio
from pykern import pkjson
from pykern.pkdebug import pkdp, pkdc
from sirepo import mpi
from sirepo import simulation_db
from sirepo.template import template_common
import os
import re
import sirepo.sim_data
import sirepo.template.flash as template
import subprocess

_SIM_DATA = sirepo.sim_data.get_class('flash')

def run_background(cfg_dir):
    mpi.run_program([pkio.py_path(cfg_dir).join(
        _SIM_DATA.flash_exe_basename(simulation_db.read_json(
            template_common.INPUT_BASE_NAME,
        )),
    )])


def units(src_path):
    res = []
    p = pkio.py_path(src_path).join('source')
    for d, _, _ in os.walk(p):
        m = re.search(
            r'^(?:{})(.*\/[A-Z0-9][A-Za-z0-9-_\.]+$)'.format(re.escape(str(p))),
            d,
        )
        if m:
            s = m.group(1)[1:]
            res.append([s, s])
    res.sort()
    pkjson.dump_pretty(res, filename='res.json')
