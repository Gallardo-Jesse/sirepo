import base64

c.Authenticator.admin_users = set(["vagrant"])
import jupyterhub.auth


class _Auth(jupyterhub.auth.Authenticator):
    async def authenticate(self, handler, data):
        if data["password"] == "testpass":
            return data["username"]
        return None


c.JupyterHub.authenticator_class = _Auth
c.JupyterHub.cleanup_servers = False
# DEPRECATED c.JupyterHub.confirm_no_ssl = True
c.JupyterHub.cookie_secret = base64.b64decode(
    "qBdGBamOJTk5REgm7GUdsReB4utbp4g+vBja0SwY2IQojyCxA+CwzOV5dTyPJWvK13s61Yie0c/WDUfy8HtU2w=="
)
# c.JupyterHub.data_files_path = '/usr/local/share/jupyterhub'
c.JupyterHub.hub_ip = "$PUBLIC_IP"
c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.port = 8000
c.JupyterHub.upgrade_db = True
c.ConfigurableHTTPProxy.auth_token = (
    "17992634c6c7489d533c1fb0ea0b95d84a6911a2076c451e1ea9041be7b63de1"
)
c.DockerSpawner.http_timeout = 60
c.DockerSpawner.image_whitelist = []
c.DockerSpawner.image = "radiasoft/beamsim-jupyter"
# c.DockerSpawner.image = 'jupyter/minimal-notebook'
c.DockerSpawner.remove = False
c.DockerSpawner.use_internal_ip = True
# Allow JupyterHub to restart without killing containers
c.DockerSpawner.network_name = "host"
c.RSDockerSpawner.cfg = """{
    "pools": {
        "private": {
            "hosts": [
                "$POOL_HOST"
            ],
            "cpu_limit": 2,
            "mem_limit": "1G",
            "shm_size": "256M",
            "min_activity_hours": 1,
            "servers_per_host": 2,
            "user_groups": [ "private" ]
        }
    },
    "port_base": 8100,
    "tls_dir": "$TLS_DIR",
    "user_groups": {
        "private": [ "vagrant" ]
    },
    "volumes": {
        "$PWD/run/user/{username}": {
            "bind": "/home/vagrant/jupyter"
        }
    }
}
"""
#        "/home/vagrant/src/radiasoft/container-jupyterhub/container-conf/rr": {
#            "bind": "/home/vagrant/.radia-run"
#        },
#        "/home/vagrant/src/radiasoft/container-jupyterhub/container-conf/jj": {
#            "bind": "/home/vagrant/.jupyter"
#        }
from rsdockerspawner import rsdockerspawner

c.JupyterHub.spawner_class = rsdockerspawner.RSDockerSpawner
c.Application.log_level = "DEBUG"
# c.JupyterHub.debug_db = True
c.ConfigurableHTTPProxy.debug = True
c.JupyterHub.log_level = "DEBUG"
c.LocalProcessSpawner.debug = True
c.Spawner.debug = True
