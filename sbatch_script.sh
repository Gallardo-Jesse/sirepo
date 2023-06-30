#!/bin/bash
#SBATCH --error=run.log
#SBATCH --ntasks=2
#SBATCH --output=run.log
#SBATCH --time=0:24:00

export SIREPO_MPI_IN_SLURM='1'
export PYTHONPATH='/home/vagrant/src/radiasoft/sirepo:/home/vagrant/src/radiasoft/pykern'
export SIREPO_MPI_CORES='2'
export SIREPO_SIM_DATA_LIB_FILE_URI='http://127.0.0.1:8102/job-cmd-lib-file/kLlsE9TSzd9MMMJIjOJbjAZg81uprMcE/'
export SIREPO_SIM_DATA_LIB_FILE_LIST='/var/tmp/user/sirepo/user/wqXeNM20/srw/wqXeNM20-TcjS8IAB-multiElectronAnimation/sirepo-lib-file-list.txt'
export SIREPO_SIM_DATA_SUPERVISOR_SIM_DB_FILE_URI='http://127.0.0.1:8102/sim-db-file/wqXeNM20/'
export SIREPO_SIM_DATA_SUPERVISOR_SIM_DB_FILE_TOKEN='H9fOQ1sz96VXIwSUiFJNTGHkzx4l3EPU'
export PYKERN_PKCONFIG_CHANNEL='dev'
export PYKERN_PKDEBUG_WANT_PID_TIME='1'
export PYTHONUNBUFFERED='1'
export SIREPO_AUTH_LOGGED_IN_USER='wqXeNM20'
export SIREPO_JOB_MAX_MESSAGE_BYTES='200000000'
export SIREPO_JOB_PING_INTERVAL_SECS='120'
export SIREPO_JOB_PING_TIMEOUT_SECS='240'
export SIREPO_JOB_VERIFY_TLS='False'
export SIREPO_SIMULATION_DB_LOGGED_IN_USER='wqXeNM20'
export SIREPO_SRDB_ROOT='/var/tmp/user/sirepo'
export PYTHONSTARTUP=''
source $HOME/.bashrc
exec srun  python parameters.py
