# -*- coding: utf-8 -*-
"""End to end test of running a job.

:copyright: Copyright (c) 2019 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function
import pytest

# TODO(e-carlin): Tests that need to be implemented
#   - agent never starts
#   - agent response is bad (ex no req_id)
#   - server_req is malformed
#   - agent starts but we never get an incoming 'read_for_work' message
#   - canceling of requests in the q and running requests
#   - using only the resources that are available
#   - agent sigterm -> sigkill progression
#   - send kill to uknown agent

def _setup(func):
    def wrapper(*args, **kwargs):
        import signal

        # ensure the test exits after a reasonable time
        signal.alarm(10)
        s = None
        try:
            env, cfg = _env_setup()
            import sirepo.srunit

            sim_type = sirepo.srunit.MYAPP
            fc = sirepo.srunit.flask_client(sim_types=sim_type, cfg=cfg)
            s = _start_job_supervisor(env)
            fc.sr_login_as_guest(sim_type)
            d = fc.sr_post(
                'listSimulations',
                {
                    'simulationType': sim_type,
                    'search': {'simulation.name': 'Scooby Doo'},
                },
            )
            d = fc.sr_get_json(
                'simulationData',
                params=dict(
                    pretty='1',
                    simulation_id=d[0].simulation.simulationId,
                    simulation_type='myapp',
                ),
            )
            func(fc, d)
        finally:
            if s:
                s.terminate()
                s.wait()
        signal.alarm(0)

    return wrapper


_REPORT = 'heightWeightReport'


@_setup
def test_runStatus(fc, sim_data):
    from pykern.pkdebug import pkdc, pkdp, pkdlog
    from sirepo import job

    run = fc.sr_post(
        'runStatus',
        dict(
            report=_REPORT,
            simulationId=sim_data.models.simulation.simulationId,
            simulationType=sim_data.simulationType,
            computeJobHash='fakeHash',
        ),
    )
    assert run.state == job.MISSING


@_setup
def test_runSimulation(fc, sim_data):
    from pykern import pkunit
    from pykern.pkdebug import pkdp
    from sirepo import job
    import time

    d = fc.sr_post(
        'runSimulation',
        dict(
            forceRun=False,
            models=sim_data.models,
            report=_REPORT,
            simulationId=sim_data.models.simulation.simulationId,
            simulationType=sim_data.simulationType,
        ),
    )
    for _ in range(10):
        assert d.state != 'error'
        if d.state == 'completed':
            break
        time.sleep(d.nextRequestSeconds)
        d = fc.sr_post('runStatus', d.nextRequest)
    else:
        pkunit.pkfail('runStatus: failed to complete: {}', d)
    # Just double-check it actually worked
    assert u'plots' in d


@_setup
def test_runCancel(fc, sim_data):
    from pykern import pkunit
    from pykern.pkdebug import pkdc, pkdp, pkdlog
    import time

    sim_data.models.simulation.name = 'srunit_long_run'
    d = fc.sr_post(
        'runSimulation',
        dict(
            forceRun=False,
            models=sim_data.models,
            report=_REPORT,
            simulationId=sim_data.models.simulation.simulationId,
            simulationType=sim_data.simulationType,
        ),
    )
    for _ in range(10):
        assert d.state != 'error'
        if d.state == 'running':
            break
        time.sleep(d.nextRequestSeconds)
        d = fc.sr_post('runStatus', d.nextRequest)
    else:
        pkunit.pkfail('runStatus: failed to start running: {}', d)

    d = fc.sr_post(
        'runCancel',
        dict(
            models=sim_data.models,
            report=_REPORT,
            simulationId=sim_data.models.simulation.simulationId,
            simulationType=sim_data.simulationType,
        )
    )
    assert d.state == 'canceled'
    d = fc.sr_post(
        'runStatus',
        # TODO(e-carlin): What actually needs to be in this dict? I just
        # copied from runSimulation
        dict(
            models=sim_data.models,
            report=_REPORT,
            simulationId=sim_data.models.simulation.simulationId,
            simulationType=sim_data.simulationType,
        ),
    )
    assert d.state == 'canceled'


def _env_setup():
    """Check if the py3 environment is set up properly"""
    import os
    import subprocess
    # DO NOT import pykern or sirepo to avoid pkconfig init too early

    cfg = {
        'PYKERN_PKDEBUG_OUTPUT': '/dev/tty',
        'PYKERN_PKDEBUG_CONTROL': 'job',
        'PYKERN_PKDEBUG_WANT_PID_TIME': '1',
        'SIREPO_FEATURE_CONFIG_JOB_SUPERVISOR': '1',
        'PYTHONUNBUFFERED': '1',
    }
    env = dict()
    for k, v in os.environ.items():
        if ('PYENV' in k or 'PYTHON' in k):
            continue
        if k in ('PATH', 'LD_LIBRARY_PATH'):
            v2 = []
            for x in v.split(':'):
                if x and 'py2' not in x:
                    v2.append(x)
            v = ':'.join(v2)
        env[k] = v
    env['PYENV_VERSION'] = 'py3'
    env.update(cfg)

    try:
        out = subprocess.check_output(
            ['pyenv', 'which', 'sirepo'],
            env=env,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        out = e.output

    assert '/py3/bin/sirepo' in out, \
        'expecting sirepo in a py3: {}'.format(out)
    try:
        out = subprocess.check_output(
            ['pyenv', 'exec', 'sirepo', 'job_supervisor', '--help'],
            env=env,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        out = e.output
    assert 'job_supervisor' in out, \
        '"job_supervisor" not in help: {}'.format(out)

    try:
        out = subprocess.check_output(
            ['pyenv', 'exec', 'sirepo', 'job_driver', '--help'],
            env=env,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        out = e.output
    assert 'job_driver' in out, \
        'job_driver not in help: {}'.format(out)

    return (env, cfg)


def _server_up(url):
    import requests
    try:
        r = requests.head(url)
        return r.status_code == 405
    except requests.ConnectionError:
        pass


def _start_job_supervisor(env):
    from pykern import pkunit
    from sirepo import srdb
    import subprocess
    import sys
    import os
    import time

    env['SIREPO_SRDB_ROOT'] = str(srdb.root())
    job_supervisor = subprocess.Popen(
        ['pyenv', 'exec', 'sirepo', 'job_supervisor'],
        env=env,
    )
    from sirepo import job
    for _ in range(30):
        if _server_up('http://127.0.0.1:8001/server'):
            break
        time.sleep(0.1)
    else:
        pkunit.pkfail('job server did not start up')
    return job_supervisor
