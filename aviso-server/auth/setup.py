# (C) Copyright 1996- ECMWF.
# 
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from aviso_auth import __version__
from setuptools import setup, find_packages
import pathlib

INSTALL_REQUIRES = (pathlib.Path(__file__).parent / "requirements.txt").read_text().splitlines()

setup(
    name='aviso-auth',
    description='Aviso-auth is a proxy designed to authenticate and authorise the listening request directed towards '
                'the store',
    version=__version__,
    url='https://git.ecmwf.int/projects/AVISO/repos/aviso/browse',
    author='ECMWF',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': [
            'aviso-auth=aviso_auth.frontend:main'
        ]
    }
)
