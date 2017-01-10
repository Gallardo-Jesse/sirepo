# -*- coding: utf-8 -*-
u"""?

:copyright: Copyright (c) 2017 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function
import pytest

pytest.importorskip('srwl_bl')

def test_create_zip():
    from pykern.pkdebug import pkdp, pkdpretty
    from pykern.pkunit import pkfail, pkok
    from pykern import pkio
    from sirepo import sr_unit
    import copy
    import zipfile

    fc = sr_unit.flask_client()
    for sim_type, sim_name, expect in (
        ('srw', 'Tabulated Undulator Example', ['magnetic_measurements.zip', 'sirepo-data.json']),
        ('elegant', 'bunchComp - fourDipoleCSR', ['magnetic_measurements.zip', 'sirepo-data.json']),
    ):
        sim_id = fc.sr_sim_data(sim_type, sim_name)['models']['simulation']['simulationId']
        res = fc.sr_get_raw(
            'exportSimulation',
            {
                'simulation_type': sim_type,
                'simulation_id': sim_id,
                'filename': 'anything.zip',
            },
        )
        with pkio.save_chdir(pkunit.work_dir()):
            fn = 'foo.zip'
            with open(fn, 'wb') as f:
                f.write(res)
            z = zipfile.ZipFile(fn)
            nl = sorted(z.namelist())
            pkok(
                nl == expect,
                '{}: zip namelist incorrect, expect={}',
                nl,
                expect,
            )
