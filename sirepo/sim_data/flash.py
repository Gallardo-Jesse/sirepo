# -*- coding: utf-8 -*-
u"""simulation data operations

:copyright: Copyright (c) 2019 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function
from pykern import pkio
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdp
from sirepo.template import template_common
import re
import sirepo.sim_data
import sirepo.simulation_db
import sirepo.util



class SimData(sirepo.sim_data.SimDataBase):

    _FLASH_EXE_PREFIX = 'flash_exe'
    _FLASH_FILE_NAME_SEP = '-'
    _FLASH_SETUP_UNITS_PREFIX = 'setup_units'

    @classmethod
    def fixup_old_data(cls, data):
        dm = data.models
        for m in list(dm.keys()):
            n = m
            for x in (':', ''), ('magnetoHD', ''), ('CapLaser$', 'CapLaserBELLA'):
                n = re.sub(x[0], x[1], n)
            if m != n:
                dm[n] = dm[m]
                del dm[m]
        cls.__fixup_old_data_setup_arguments(data)
        cls._init_models(dm)
        if dm.simulation.flashType == 'CapLaser':
            dm.simulation.flashType = 'CapLaserBELLA'
        if dm.simulation.flashType == 'CapLaserBELLA':
            dm.IO.update(
                plot_var_5='magz',
                plot_var_6='depo',
            )
            if not dm.Multispecies.ms_fillSpecies:
                m = dm.Multispecies
                m.ms_fillSpecies = 'hydrogen'
                m.ms_wallSpecies = 'alumina'
                m.eos_fillTableFile = 'helium-fill-imx.cn4'
                m.eos_wallTableFile = 'alumina-wall-imx.cn4'
                m.eos_fillSubType = 'ionmix4'
                m.eos_wallSubType = 'ionmix4'
                m = dm['physicsmaterialPropertiesOpacityMultispecies']
                m.op_fillFileName = 'helium-fill-imx.cn4'
                m.op_wallFileName  = 'alumina-wall-imx.cn4'
                m.op_fillFileType = 'ionmix4'
                m.op_wallFileType = 'ionmix4'
        dm['physicssourceTermsEnergyDepositionLaser'].pkdel('ed_gridnAngularTics_1')
        for n in 'currType', 'eosFill', 'eosWall':
            dm.pkdel(f'SimulationCapLaserBELLA{n}')
        m = dm.physicssourceTermsHeatexchange
        if 'useHeatExchange' in m:
            m.useHeatexchange = m.useHeatExchange
            m.pkdel('useHeatExchange')
        m = dm.gridEvolutionAnimation
        if 'valueList' not in m:
            m.valueList = PKDict()
            for x in 'y1', 'y2', 'y3':
                if dm.simulation.flashType in ('CapLaserBELLA', 'CapLaser3D'):
                    m.valueList[x] = [
                        'mass',
                        'x-momentum',
                        'y-momentum',
                        'z-momentum',
                        'E_total',
                        'E_kinetic',
                        'E_internal',
                        'MagEnergy',
                        'r001',
                        'r002',
                        'r003',
                        'r004',
                        'r005',
                        'r006',
                        'sumy',
                        'ye',
                    ]
                elif dm.simulation.flashType == 'RTFlame':
                    m.valueList[x] = [
                        'mass',
                        'x-momentum',
                        'y-momentum',
                        'z-momentum',
                        'E_total',
                        'E_kinetic',
                        'E_turbulent',
                        'E_internal',
                        'Burned Mass',
                        'dens_burning_ave',
                        'db_ave samplevol',
                        'Burning rate',
                        'fspd to input_fspd ratio',
                        'surface area flam=0.1',
                        'surface area flam=0.5',
                        'surface area flam=0.9',
                    ]

    @classmethod
    def flash_exe_basename(cls, data):
        return cls._flash_file_basename(
            cls._FLASH_EXE_PREFIX,
            data,
        )

    @classmethod
    def flash_setup_units_basename(cls, data):
        return cls._flash_file_basename(cls._FLASH_SETUP_UNITS_PREFIX, data)

    @classmethod
    def proprietary_code_rpm(cls):
        return cls._proprietary_code_rpm()

    @classmethod
    def sim_files_to_run_dir(cls, data, run_dir):
        try:
            super().sim_files_to_run_dir(data, run_dir)
        except sirepo.sim_data.SimDbFileNotFound:
            cls._flash_create_sim_files(data, run_dir)

    @classmethod
    def _compute_job_fields(cls, data, r, compute_model):
        return [r]

    @classmethod
    def _flash_create_sim_files(cls, data, run_dir):
        import sirepo.mpi
        import sirepo.template.flash
        import subprocess

        with open(cls.lib_file_abspath(cls.proprietary_code_rpm())) as i:
            subprocess.check_output(
                "rpm2cpio - | cpio --extract --make-directories",
                cwd='/',
                #SECURITY: No user defined input in cmd so shell=True is ok
                shell=True,
                stderr=subprocess.STDOUT,
                stdin=i,
            )
        subprocess.check_output(
            [
                'tar',
                '--extract',
                '--gunzip',
                f'--file={cls._sim_src_tarball_path()}',
                f'--directory={run_dir}',
            ],
            stderr=subprocess.STDOUT,
        )
        s = run_dir.join(cls.sim_type())
        t = s.join(data.models.simulation.flashType)
        with run_dir.join(template_common.COMPILE_LOG).open('w') as log:
            k = PKDict(
                check=True,
                stdout=log,
                stderr=log
            )
            subprocess.run(sirepo.template.flash.setup_command(data), cwd=s, **k)
            subprocess.run(['make', f'-j{sirepo.mpi.cfg.cores}'], cwd=t, **k)
        for c, b in PKDict(
                # POSIT: values match cls._sim_file_basenames
                flash4=cls.flash_exe_basename(data),
                setup_units=cls.flash_setup_units_basename(data),
        ).items():
            p = t.join(c)
            cls.delete_sim_file(cls._flash_file_prefix(b), data)
            cls.put_sim_file(p, b, data)
            p.move(run_dir.join(b))

    @classmethod
    def _flash_file_basename(cls, prefix, data):
        return prefix + cls._FLASH_FILE_NAME_SEP + cls._flash_file_hash(data)

    @classmethod
    def _flash_file_hash(cls, data):
        return sirepo.util.url_safe_hash(str((
            data.models.simulation.flashType,
            data.models.setupArguments,
        )))

    @classmethod
    def _flash_file_prefix(cls, basename):
        return basename.split(cls._FLASH_FILE_NAME_SEP)[0]

    @classmethod
    def _lib_file_basenames(cls, data):
        t = data.models.simulation.flashType
        if t == 'RTFlame':
            return ['helm_table.dat']
        if 'CapLaser' in t:
            r = [
                'alumina-wall-imx.cn4',
                'argon-fill-imx.cn4',
                'helium-fill-imx.cn4',
                'hydrogen-fill-imx.cn4',
            ]
            if t == 'CapLaserBELLA'  and data.models['SimulationCapLaserBELLA'].sim_currType == '2':
                r.append(cls.lib_file_name_with_model_field(
                    'SimulationCapLaserBELLA',
                    'sim_currFile',
                    data.models['SimulationCapLaserBELLA'].sim_currFile,
                ))
            return r
        raise AssertionError('invalid flashType: {}'.format(t))

    @classmethod
    def _sim_file_basenames(cls, data):
        return [
            PKDict(basename=cls.flash_exe_basename(data), is_exe=True),
            PKDict(basename=cls.flash_setup_units_basename(data)),
        ]

    @classmethod
    def __fixup_old_data_setup_arguments(cls, data):
        dm = data.models
        if 'setupArguments' in dm:
            return
        for e in sirepo.simulation_db.examples(cls.sim_type()):
            if e.models.simulation.flashType == dm.simulation.flashType:
                dm.setupArguments = e.models.setupArguments
                return
