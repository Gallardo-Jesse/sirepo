# -*- coding: utf-8 -*-
"""Run Python processes in background

:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function
from pykern import pkconfig
from pykern import pkio
from pykern.pkdebug import pkdc, pkdexc, pkdp
import os
import re
import signal
import subprocess
import sys


def run_program(cmd, output='mpi_run.out', env=None):
    """Execute python script with mpi.

    Args:
        cmd (list): cmd to run
        output (str): where to write stdout and stderr
        env (dict): what to pass as env
    """
    p = None
    from sirepo import simulation_db
    try:
        cmd = [
            'mpiexec',
            '--bind-to',
            'none',
            '-n',
            str(cfg.cores),

        ] + cmd
        p = subprocess.Popen(
            cmd,
            stdin=open(os.devnull),
            stdout=open(output, 'w'),
            stderr=subprocess.STDOUT,
            env=env,
        )
        pkdp('Started: {} {}', p.pid, cmd)
        signal.signal(signal.SIGTERM, lambda x, y: p.terminate())
        rc = p.wait()
        if rc != 0:
            p = None
            raise RuntimeError('child terminated: retcode={}'.format(rc))
        pkdp('Stopped: {} {}', p.pid, cmd)
        p = None
    except BaseException as e:
        #TODO: Clean result?? Just an exception as string
        simulation_db.write_result({'state': 'error', 'error': str(e)})
        pkdp('Exception: {} {} {}: ', p.pid if p else None, cmd, pkdexc())
        raise
    finally:
        if not p is None:
            pkdp('Terminating: {} {}', p.pid, cmd)
            p.terminate()


def run_script(script):
    """Execute python script with mpi.

    Args:
        script (str): python text
    """
    abort = '''

from mpi4py import MPI
if MPI.COMM_WORLD.Get_rank():
    import signal
    signal.signal(signal.SIGTERM, lambda x, y: MPI.COMM_WORLD.Abort(1))

'''
    n = re.sub(r'^from __future.*', abort, script, count=1, flags=re.MULTILINE)
    script = abort + script if n == script else n
    fn = 'mpi_run.py'
    pkio.write_text(fn, script)
    p = None
    return run_program([sys.executable or 'python', fn])


cfg = pkconfig.init(
    cores=(1, int, 'cores to use per run'),
    slaves=(1, int, 'DEPRECATED: set $SIREPO_MPI_CORES'),
)
cfg.cores = max(cfg.cores, cfg.slaves)
