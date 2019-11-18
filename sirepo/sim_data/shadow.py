# -*- coding: utf-8 -*-
u"""simulation data operations

:copyright: Copyright (c) 2019 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function
from pykern.pkdebug import pkdc, pkdlog, pkdp
import sirepo.sim_data


class SimData(sirepo.sim_data.SimDataBase):

    ANALYSIS_ONLY_FIELDS = frozenset(('colorMap', 'notes', 'aspectRatio'))

    @classmethod
    def fixup_old_data(cls, data):
        dm = data.models
        if (
            float(data.fixup_old_version) < 20170703.000001
            and 'geometricSource' in dm
        ):
            g = data.models.geometricSource
            x = g.cone_max
            g.cone_max = g.cone_min
            g.cone_min = x
        cls._init_models(dm, ('initialIntensityReport', 'plotXYReport'))
        for m in dm:
            if cls.is_watchpoint(m):
                cls.update_model_defaults(dm[m], 'watchpointReport')
        cls._organize_example(data)

    @classmethod
    def resource_files(cls):
        return cls.resource_glob('*.txt')

    @classmethod
    def shadow_simulation_files(cls, data):
        m = data.models
        if m.simulation.sourceType == 'wiggler' && m.wiggler.b_from in ('1', '2'):
            return [cls.shadow_wiggler_file(m.wiggler.trajFile)]
        return []

    @classmethod
    def shadow_wiggler_file(cls, value):
        return cls.lib_file_name('wiggler', 'trajFile', value)

    @classmethod
    def _compute_job_fields(cls, data):
        r = data['report']
        res = cls._non_analysis_fields(data, r) + [
            'bendingMagnet',
            'electronBeam',
            'geometricSource',
            'rayFilter',
            'simulation.istar1',
            'simulation.npoint',
            'simulation.sourceType',
            'sourceDivergence',
            'wiggler',
        ]
        if r == 'initialIntensityReport' and len(data['models']['beamline']):
            res.append([data['models']['beamline'][0]['position']])
        #TODO(pjm): only include items up to the current watchpoint
        if cls.is_watchpoint(r):
            res.append('beamline')
        return res

    @classmethod
    def _lib_files(cls, data, *args, **kwargs):
        return _cls.shadow_simulation_files(data)
