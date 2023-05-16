# -*- coding: utf-8 -*-
"""epicsllrf execution template.

:copyright: Copyright (c) 2017-2018 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from pykern import pkio
from pykern import pkjinja
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdp
from sirepo import simulation_db
from sirepo.template import template_common
import filecmp
import os
import re
import shutil
import sirepo.sim_data
import sirepo.util

_STATUS_FILE = "status.json"
_SIM_DATA, SIM_TYPE, SCHEMA = sirepo.sim_data.template_globals()


def background_percent_complete(report, run_dir, is_running):
    return PKDict(
        percentComplete=100,
        frameCount=0,
        hasEpicsData=run_dir.join(_STATUS_FILE).exists(),
    )


def epics_env(server_address):
    env = os.environ.copy()
    env["EPICS_CA_AUTO_ADDR_LIST"] = "NO"
    env["EPICS_CA_ADDR_LIST"] = server_address
    env["EPICS_CA_SERVER_PORT"] = server_address.split(":")[1]
    return env


def python_source_for_model(data, model, qcall, **kwargs):
    return _generate_parameters_file(data)


def stateless_compute_read_epics_values(data, **kwargs):
    _PREV_EPICS_FILE = "prev-status.json"
    # TODO(pjm): hacked in animation directory
    run_dir = pkio.py_path(
        re.sub(r"/unused$", "/animation", str(simulation_db.simulation_run_dir(data)))
    )
    p = run_dir.join(_PREV_EPICS_FILE)
    e = run_dir.join(_STATUS_FILE)
    if (
        not data.get("noCache")
        and e.exists()
        and p.exists()
        and filecmp.cmp(str(e), str(p), False)
    ):
        return PKDict()
    shutil.copyfile(str(e), str(p))
    return PKDict(
        epicsData=_read_epics_data(run_dir),
    )


def write_parameters(data, run_dir, is_parallel):
    pkio.write_text(
        run_dir.join(template_common.PARAMETERS_PYTHON_FILE),
        _generate_parameters_file(data),
    )


def _generate_parameters_file(data):
    res, v = template_common.generate_parameters_file(data)
    v.statusFile = _STATUS_FILE
    return template_common.render_jinja(
        SIM_TYPE,
        v,
        template_common.PARAMETERS_PYTHON_FILE,
    )


def _read_epics_data(run_dir):
    s = run_dir.join(_STATUS_FILE)
    if s.exists():
        d = simulation_db.json_load(s)
        for f in d:
            v = d[f][0]
            if re.search(r"[A-Za-z]{2}", v):
                v = re.sub(r"\(\d+\)", "", v)
            elif v[0] == "[":
                v = re.sub(r"\[|\]", "", v)
                v = [float(x) for x in v.split(",")]
            else:
                v = float(v)
            d[f] = v
        d = _check_connection(d)
        return d
    return PKDict()


def _check_connection(process_variables):
    for k in process_variables:
        if type(process_variables[k]) == float:
            continue
        for e in (
            PKDict(value="disconnected", error="Disconnected from EPICS"),
            PKDict(value="(PV not found)", error="No EPICS process found"),
        ):
            if e.value in process_variables[k]:
                return PKDict(error=e.error)
    return process_variables
