# -*- coding: utf-8 -*-
u"""SRW execution template.

:copyright: Copyright (c) 2015 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
#TODO(robnagler) fix up old data(?) probably just remove
#TODO(robnagler) fix up other simulations to use template_common(?)

from __future__ import absolute_import, division, print_function
from opmd_viewer import OpenPMDTimeSeries
from opmd_viewer.openpmd_timeseries import main
from opmd_viewer.openpmd_timeseries.data_reader import field_reader
from pykern import pkcollections
from pykern import pkio
from pykern import pkjinja
from pykern.pkdebug import pkdc, pkdp
from sirepo import simulation_db
from sirepo.template import template_common
import h5py
import numpy
import os
import os.path
import py.path
import re

WANT_BROWSER_FRAME_CACHE = True

_MIN_MAX_INDEX = {
    'x': [3, 4],
    'y': [5, 6],
    'z': [7, 8],
    'ux': [9, 10],
    'uy': [11, 12],
    'uz': [13, 14],
}


def background_percent_complete(report, run_dir, is_running, schema):
    files = _h5_file_list(run_dir)
    if len(files) < 2:
        return {
            'percentComplete': 0,
            'frameCount': 0,
        }
    file_index = len(files) - 1
    last_update_time = int(os.path.getmtime(str(files[file_index])))
    # look at 2nd to last file if running, last one may be incomplete
    if is_running:
        file_index -= 1
    data = simulation_db.read_json(run_dir.join(template_common.INPUT_BASE_NAME))
    Fr, info = field_reader.read_field_circ(str(files[file_index]), 'E/r')
    plasma_length = float(data['models']['electronPlasma']['length']) / 1e3
    zmin = float(data['models']['simulationGrid']['zMin']) / 1e6
    percent_complete = (info.imshow_extent[1] / (plasma_length - zmin))
    if percent_complete < 0:
        percent_complete = 0
    elif percent_complete > 1.0:
        percent_complete = 1.0
    return {
        'lastUpdateTime': last_update_time,
        'percentComplete': percent_complete * 100,
        'frameCount': file_index + 1,
    }


def copy_related_files(data, source_path, target_path):
    pass


def extract_field_report(field, coordinate, mode, data_file):
    opmd = _opmd_time_series(data_file)
    F, info = opmd.get_field(
        plot=False,
        vmin=None,
        m=mode,
        coord=coordinate,
        iteration=data_file.iteration,
        slicing=0.0,
        field=field,
        theta=0.0,
        vmax=None,
        output=True,
        slicing_dir='y',

    )
    extent = info.imshow_extent
    if field == 'rho':
        field_label = field
    else:
        field_label = '{} {}'.format(field, coordinate)
    return {
        'x_range': [extent[0], extent[1], len(F[0])],
        'y_range': [extent[2], extent[3], len(F)],
        'x_label': '{} [m]'.format(info.axes[1]),
        'y_label': '{} [m]'.format(info.axes[0]),
        'title': "{} in the mode {} at {}".format(
            field_label, mode, _iteration_title(opmd, data_file)),
        'z_matrix': numpy.flipud(F).tolist(),
    }


def extract_particle_report(args, particle_type, run_dir, data_file):
    xarg = args[0]
    yarg = args[1]
    histogram_bins = args[2]
    opmd = _opmd_time_series(data_file)
    data_list = opmd.get_particle(
        var_list=[xarg, yarg],
        species=particle_type,
        iteration=data_file.iteration,
        select=None,
        output=True,
        plot=False,
    )
    with h5py.File(data_file.filename) as f:
        data_list.append(main.read_species_data(f, particle_type, 'w', ()))
    select = _particle_selection_args(args)
    if select:
        with h5py.File(data_file.filename) as f:
            main.apply_selection(f, data_list, select, particle_type, ())
    xunits = ' [m]' if len(xarg) == 1 else ''
    yunits = ' [m]' if len(yarg) == 1 else ''
    if len(data_list[0]) < 2:
        return {
            'x_range': [0, 1e-6, 2],
            'y_range': [0, 1e-6, 2],
            'x_label': '{}{}'.format(xarg, xunits),
            'y_label': '{}{}'.format(yarg, yunits),
            'title': 't = {}'.format(_iteration_title(opmd, data_file)),
            'z_matrix': [[0, 0], [0, 0]],
            'frameCount': data_file.num_frames,
        }
    if len(xarg) == 1:
        data_list[0] /= 1e6
    if len(yarg) == 1:
        data_list[1] /= 1e6

    if xarg == 'z':
        data_list = _adjust_z_width(data_list, data_file)

    hist, edges = numpy.histogramdd([data_list[0], data_list[1]], int(histogram_bins), weights=data_list[2])
    return {
        'x_range': [float(edges[0][0]), float(edges[0][-1]), len(hist)],
        'y_range': [float(edges[1][0]), float(edges[1][-1]), len(hist[0])],
        'x_label': '{}{}'.format(xarg, xunits),
        'y_label': '{}{}'.format(yarg, yunits),
        'title': 't = {}'.format(_iteration_title(opmd, data_file)),
        'z_matrix': hist.T.tolist(),
        'frameCount': data_file.num_frames,
    }


def fixup_old_data(data):
    if 'laserPreviewReport' not in data['models']:
        data['models']['laserPreviewReport'] = {}
    if 'particleAnimation' not in data['models']:
        data['models']['particleAnimation'] = {
            'x': 'z',
            'y': 'x',
            'histogramBins': 100,
        }
    if 'simulationStatus' not in data['models']:
        data['models']['simulationStatus'] = {}
    if 'histogramBins' not in data['models']['particleAnimation']:
        data['models']['particleAnimation']['histogramBins'] = 100
    if 'framesPerSecond' not in data['models']['fieldAnimation']:
        data['models']['fieldAnimation']['framesPerSecond'] = 20
        data['models']['particleAnimation']['framesPerSecond'] = 20
    if 'rScale' not in data['models']['simulationGrid']:
        grid = data['models']['simulationGrid']
        grid['rScale'] = 4
        grid['rLength'] = '20.324980154380'
        grid['rMin'] = 0
        grid['rMax'] = '20.324980154380'
        grid['rCellsPerSpotSize'] = 8
        grid['rCount'] = 32
        grid['zScale'] = 2
        grid['zLength'] = '20.324980154631'
        grid['zMin'] = '-20.324980154631'
        grid['zMax'] = '1.60'
        grid['zCellsPerWavelength'] = 8
        grid['zCount'] = 214
        del grid['xMin']
        del grid['xMax']
        del grid['xCount']
        del grid['zLambda']
    if 'rParticlesPerCell' not in data['models']['simulationGrid']:
        data['models']['simulationGrid']['rParticlesPerCell'] = 1
        data['models']['simulationGrid']['zParticlesPerCell'] = 2
    if 'field' not in data['models']['laserPreviewReport']:
        laserPreview = data['models']['laserPreviewReport']
        laserPreview['field'] = 'E'
        laserPreview['coordinate'] = 'y'
        laserPreview['mode'] = '1'
    if 'sourceType' not in data['models']['simulation']:
        data['models']['simulation']['sourceType'] = 'laserPulse'
    if 'electronBeam' not in data['models']:
        data['models']['electronBeam'] = {
            'charge': 1.0e-08,
            'energy': 23,
        }
    if 'beamPreviewReport' not in data['models']:
        data['models']['beamPreviewReport'] = {
            'x': 'z',
            'y': 'x',
            'histogramBins': 100
        }
    if 'beamAnimation' not in data['models']:
        data['models']['beamAnimation'] = data['models']['particleAnimation'].copy()
    if 'rCellResolution' not in data['models']['simulationGrid']:
        grid = data['models']['simulationGrid']
        grid['rCellResolution'] = 40
        grid['zCellResolution'] = 40
    if 'rmsLength' not in data['models']['electronBeam']:
        beam = data['models']['electronBeam']
        beam['rmsLength'] = 0
        beam['rmsRadius'] = 0
        beam['bunchLength'] = 0
        beam['transverseEmittance'] = 0
    if 'xMin' not in data['models']['particleAnimation']:
        animation = data['models']['particleAnimation']
        for v in ('x', 'y', 'z'):
            animation['{}Min'.format(v)] = 0
            animation['{}Max'.format(v)] = 0
            animation['u{}Min'.format(v)] = 0
            animation['u{}Max'.format(v)] = 0
    if 'beamRadiusMethod' not in data['models']['electronBeam']:
        beam = data['models']['electronBeam']
        beam['beamRadiusMethod'] = 'a'
        beam['transverseEmittance'] = 0.00001
        beam['rmsRadius'] = 15
        beam['beamBunchLengthMethod'] = 's'
    if 'folder' not in data['models']['simulation']:
        data['models']['simulation']['folder'] = '/'


def generate_parameters_file(data, schema, run_dir=None, is_parallel=False):
    _validate_data(data, schema)
    v = template_common.flatten_data(data['models'], {})
    v['outputDir'] = '"{}"'.format(run_dir) if run_dir else None
    v['isAnimationView'] = is_parallel
    v['incSteps'] = 50
    v['diagnosticPeriod'] = 50
    if data['models']['simulation']['sourceType'] == 'electronBeam':
        v['useBeam'] = 1
        v['useLaser'] = 0
    else:
        v['useBeam'] = 0
        v['useLaser'] = 1
    if data['models']['electronBeam']['beamRadiusMethod'] == 'a':
        v['electronBeam_transverseEmittance'] = 0
    return pkjinja.render_resource('warp.py', v)


def get_animation_name(data):
    return 'animation'


def get_simulation_frame(run_dir, data, model_data):
    frame_index = int(data['frameIndex'])
    data_file = open_data_file(run_dir, frame_index)
    args = data['animationArgs'].split('_')
    if data['modelName'] == 'fieldAnimation':
        return _field_animation(args, data_file)
    if data['modelName'] == 'particleAnimation':
        return extract_particle_report(args, 'electrons', run_dir, data_file)
    if data['modelName'] == 'beamAnimation':
        return extract_particle_report(args, 'beam', run_dir, data_file)
    raise RuntimeError('{}: unknown simulation frame model'.format(data['modelName']))


def get_data_file(run_dir, model, frame):
    files = _h5_file_list(run_dir)
    #TODO(pjm): last client file may have been deleted on a canceled animation,
    # give the last available file instead.
    if len(files) < frame + 1:
        frame = -1
    filename = str(files[int(frame)])
    with open(filename) as f:
        return os.path.basename(filename), f.read(), 'application/octet-stream'


def models_related_to_report(data):
    """What models are required for this data['report']

    Args:
        data (dict): simulation
    Returns:
        list: Named models that affect report or [] if don't know
    """
    if not (data['report'] in ('beamPreviewReport', 'laserPreviewReport')):
        return []
    return [
        'electronBeam',
        'electronPlasma',
        'laserPulse',
        'simulationGrid',
    ]


def new_simulation(data, new_simulation_data):
    source = new_simulation_data['sourceType']
    if not source:
        source = 'laserPulse'
    data['models']['simulation']['sourceType'] = source
    if source == 'electronBeam':
        grid = data['models']['simulationGrid']
        grid['gridDimensions'] = 'e'
        grid['rCellResolution'] = 20
        grid['rCellsPerSpotSize'] = 8
        grid['rCount'] = 100
        grid['rLength'] = 264.0501846240597
        grid['rMax'] = 264.0501846240597
        grid['rMin'] = 0
        grid['rParticlesPerCell'] = 2
        grid['rScale'] = 5
        grid['zCellResolution'] = 30
        grid['zCellsPerWavelength'] = 8
        grid['zCount'] = 90
        grid['zLength'] = 316.86022154887166
        grid['zMax'] = 0
        grid['zMin'] = -316.86022154887166
        grid['zParticlesPerCell'] = 2
        grid['zScale'] = 3
        data['models']['electronPlasma']['density'] = 1e23
        data['models']['electronPlasma']['length'] = 1
        data['models']['fieldAnimation']['coordinate'] = 'z'
        data['models']['fieldAnimation']['mode'] = '0'
        data['models']['particleAnimation']['histogramBins'] = 90
        data['models']['particleAnimation']['yMin'] = -50
        data['models']['particleAnimation']['yMax'] = 50
        data['models']['beamAnimation']['histogramBins'] = 91
        data['models']['beamPreviewReport']['histogramBins'] = 91


def open_data_file(run_dir, file_index=None):
    """Opens data file_index'th in run_dir

    Args:
        run_dir (py.path): has subdir ``hdf5``
        file_index (int): which file to open (default: last one)
        files (list): list of files (default: load list)

    Returns:
        OrderedMapping: various parameters
    """
    files = _h5_file_list(run_dir)
    res = pkcollections.OrderedMapping()
    res.num_frames = len(files)
    res.frame_index = res.num_frames - 1 if file_index is None else file_index
    res.filename = str(files[res.frame_index])
    res.iteration = int(re.search(r'data(\d+)', res.filename).group(1))
    return res


def prepare_aux_files(run_dir, data):
    pass


def prepare_for_client(data):
    return data


def remove_last_frame(run_dir):
    files = _h5_file_list(run_dir)
    if len(files) > 0:
        pkio.unchecked_remove(files[-1])


def run_all_text():
    return ''


def validate_file(file_type, path):
    return None


def write_parameters(data, schema, run_dir, is_parallel):
    """Write the parameters file

    Args:
        data (dict): input
        schema (dict): to validate data
        run_dir (py.path): where to write
        is_parallel (bool): run in background?
    """
    pkio.write_text(
        run_dir.join(template_common.PARAMETERS_PYTHON_FILE),
        generate_parameters_file(
            data,
            schema,
            run_dir,
            is_parallel,
        ),
    )


def static_lib_files():
    """Library shared between simulations of this type

    Returns:
        list: py.path.local objects
    """
    return []


def _adjust_z_width(data_list, data_file):
    # match boundaries with field report
    Fr, info = field_reader.read_field_circ(data_file.filename, 'E/r')
    extent = info.imshow_extent
    return [
        numpy.append(data_list[0], [extent[0], extent[1]]),
        numpy.append(data_list[1], [extent[2], extent[3]]),
        numpy.append(data_list[2], [0, 0]),
    ]


def _field_animation(args, data_file):
    field = args[0]
    coordinate = args[1]
    mode = args[2]
    if mode != 'all':
        mode = int(mode)
    res = extract_field_report(field, coordinate, mode, data_file)
    res['frameCount'] = data_file.num_frames
    return res


def _h5_file_list(run_dir):
    return pkio.walk_tree(
        run_dir.join('hdf5'),
        r'\.h5$',
    )


def _iteration_title(opmd, data_file):
    fs = opmd.t[0] * 1e15
    return '{:.1f} fs (iteration {})'.format(fs, data_file.iteration)


def _opmd_time_series(data_file):
    prev = None
    try:
        prev = main.list_h5_files
        main.list_h5_files = lambda x: ([data_file.filename], [data_file.iteration])
        return OpenPMDTimeSeries(py.path.local(data_file.filename).dirname)
    finally:
        if prev:
            main.list_h5_files = prev


def _particle_selection_args(args):
    if len(args) <= 3:
        return None
    res = {}
    for f in ('', 'u'):
        for f2 in ('x', 'y', 'z'):
            field = '{}{}'.format(f, f2)
            min_max_index = _MIN_MAX_INDEX[field]
            min = float(args[min_max_index[0]])
            max = float(args[min_max_index[1]])
            if min == 0 and max == 0:
                continue
            res[field] = [min, max]
    return res if len(res.keys()) else None


def _validate_data(data, schema):
    # ensure enums match, convert ints/floats, apply scaling
    enum_info = template_common.parse_enums(schema['enum'])
    for k in data['models']:
        if k in schema['model']:
            template_common.validate_model(data['models'][k], schema['model'][k], enum_info)
