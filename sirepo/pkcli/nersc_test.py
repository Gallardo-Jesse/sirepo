# -*- coding: utf-8 -*-
"""Allow NERSC to run tests of Sirepo images in their infrastructure

:copyright: Copyright (c) 2023 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdp, pkdlog
import os
import pykern.pkio
import pykern.pkjinja
import pykern.pkjson
import sirepo.const
import sirepo.resource
import sirepo.sim_data
import subprocess


def parallel():
    def _render_resource(run_dir, filename):
        res = run_dir.join(filename)
        pykern.pkjinja.render_file(
            sirepo.resource.file_path(
                "nersc_test/" + filename + pykern.pkjinja.RESOURCE_SUFFIX
            ),
            PKDict(run_dir=run_dir),
            output=res,
        )
        return res

    d = pykern.pkio.py_path("sirepo_run_dir")
    pykern.pkio.unchecked_remove(d)
    d.ensure(dir=True)
    _render_resource(d, "parameters.py")
    p = subprocess.run(
        ["sbatch", _render_resource(d, "sbatch_script.sh")]
    )
    return "nersc_test.parallel PASS"


def sequential(pkunit_deviance=None):
    """Test sequential process for use by NERSC inside SHIFTER

    Simulates the operation that Sirepo does when it executes a
    sequential process on a login node in SHIFTER.

    On success, will return (output) ``nersc_test.sequential PASS``

    Args:
        pkunit_deviance (str): used only by internal unit test to test deviance case

    Returns:
        str: PASS or fail with diagnostic information
    """
    s = _Sequential()
    try:
        s.prepare(pkunit_deviance)
        s.execute()
        return "nersc_test.sequential PASS"
    except Exception as e:
        return f"nersc_test sequential fail: error={e}\nunix_uid={os.geteuid()}\n{s}{pkdexc()}"


class _Sequential(PKDict):
    """Run a sequential job by mocking the input to job_cmd"""

    JOB_CMD_FILE = "sequential_job_cmd.json"
    RESOURCE_DIR = "nersc_test/"
    RESULT_FILE = "sequential_result.json"
    RUN_DIR = "sirepo_run_dir"
    RUN_FILE = "sequential_run.sh"

    def prepare(self, pkunit_deviance):
        self.pkunit_deviance = pkunit_deviance
        self.run_dir = pykern.pkio.py_path(self.RUN_DIR)
        pykern.pkio.unchecked_remove(self.run_dir)
        self.run_dir.ensure(dir=True)
        self.result_file = self.run_dir.join(self.RESULT_FILE)
        self.user = sirepo.const.MOCK_UID
        # job_cmd_file must be first, because used by _render_resource
        self.job_cmd_file = self._job_cmd_file()
        self.run_file = self._render_resource(self.RUN_FILE)

    def execute(self):
        p = subprocess.run(["bash", self.run_file], capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(
                f"unexpected returncode={p.returncode} stderr={p.stderr}"
            )
        self.result_file.write(p.stdout)
        self.result_text = p.stdout
        self.result_parsed = pykern.pkjson.load_any(self.result_text)
        if self.result_parsed.state != "completed":
            raise RuntimeError(f"unexpected result state={self.result_parsed.state}")

    def _file_path(self, filename):
        return sirepo.resource.file_path(
            self.RESOURCE_DIR + filename + pykern.pkjinja.RESOURCE_SUFFIX
        )

    def _job_cmd_file(self):
        if self.pkunit_deviance:
            return pykern.pkio.py_path(self.pkunit_deviance)
        return self._render_resource(self.JOB_CMD_FILE)

    def __str__(self):
        res = "Internal state:\n"
        for k in ("run_dir", "run_file", "result_file"):
            res += f"{k}={self.get(k)}\n"
        if "result_text" in self:
            if "result_parsed" in self:
                res += "result_parsed=" + pykern.pkjson.dump_pretty(self.result_parsed)
            else:
                res += "result_text=" + self.result_text
        return res

    def _render_resource(self, filename):
        res = self.run_dir.join(filename)
        pykern.pkjinja.render_file(
            self._file_path(filename),
            PKDict(
                job_cmd_file=self.get("job_cmd_file"),
                run_dir=self.run_dir,
                user=self.user,
            ),
            output=res,
        )
        return res
