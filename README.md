# ![Sirepo](https://github.com/radiasoft/images/blob/master/sirepo/Sirepo_logo.png)

<p align="center">

## Sirepo brings computational science to the cloud.

Develop, run and share your HPC simulations.
</p>

Sirepo brings Clickable Physics(TM) to your desktop and mobile devices.

[Try our public Sirepo server](https://www.sirepo.com).

No signup is required and Sirepo is completely free.

## If you prefer, Sirepo can also be downloaded! :arrow_down:
1. [Curl Installer for Mac and Linux](#curl-installer)
2. [Manual Install with Docker](#manual-install-with-docker)
3. [Development](https://github.com/radiasoft/sirepo/wiki/Development)

## Curl Installer

You can use our
[curl installer on your Mac, PC (Cygwin only), or Linux box](https://github.com/radiasoft/download/blob/master/README.md)
as follows:

```bash
$ mkdir sirepo
$ cd sirepo
$ curl radia.run | bash -s sirepo
```

For this to work, you will need to [install the prerequisites](https://github.com/radiasoft/download/blob/master/README.md#requirements).

[API Documentation is available on Read the Docs.](http://sirepo.readthedocs.org)

## Manual Install with Docker

You can start Sirepo with [Docker](https://www.docker.com/).

If you are running Docker as an ordinary user (recommended), use the following:

```bash
$ docker run --rm -p 8000:8000 -v "$PWD:/sirepo" radiasoft/sirepo
```

Then visit: http://127.0.0.1:8000

The `-v "$PWD:/sirepo"` creates a `db` subdirectory, which is where the database is stored.

# License

License: http://www.apache.org/licenses/LICENSE-2.0.html

Copyright (c) 2015-2018 [RadiaSoft LLC](http://radiasoft.net/open-source).  All Rights Reserved.

![RadiaSoft](https://github.com/radiasoft/images/blob/master/corporate/RadiaSoftLogoTransparent.png)
