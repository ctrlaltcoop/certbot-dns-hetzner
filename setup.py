from distutils.version import LooseVersion
import os
import sys

from setuptools import __version__ as setuptools_version
from setuptools import find_packages
from setuptools import setup

version = '1.0.5'

# This package relies on PyOpenSSL, requests, and six, however, it isn't
# specified here to avoid masking the more specific request requirements in
# acme. See https://github.com/pypa/pip/issues/988 for more info.
install_requires = [
    'setuptools',
    'zope.interface',
    'requests',
    'mock',
    'requests-mock',
    'parsedatetime<=2.5;python_version<"3.0"'
]

if not os.environ.get('SNAP_BUILD'):
    install_requires.extend([
        'acme>=0.31.0',
        'certbot>=1.1.0',
    ])
elif 'bdist_wheel' in sys.argv[1:]:
    raise RuntimeError('Unset SNAP_BUILD when building wheels '
                       'to include certbot dependencies.')
if os.environ.get('SNAP_BUILD'):
    install_requires.append('packaging')

setuptools_known_environment_markers = (LooseVersion(setuptools_version) >= LooseVersion('36.2'))
if setuptools_known_environment_markers:
    install_requires.append('mock ; python_version < "3.3"')
elif 'bdist_wheel' in sys.argv[1:]:
    raise RuntimeError('Error, you are trying to build certbot wheels using an old version '
                       'of setuptools. Version 36.2+ of setuptools is required.')
elif sys.version_info < (3,3):
    install_requires.append('mock')

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(BASE_PATH, "README.md")) as f:
    long_description = f.read()

setup(
    name='certbot-dns-hetzner',
    version=version,
    description="Hetzner DNS Authenticator plugin for Certbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/ctrlaltcoop/certbot-dns-hetzner',
    author="ctrl.alt.coop",
    author_email='kontakt@ctrl.alt.coop',
    license='Apache License 2.0',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],

    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'certbot.plugins': [
            'dns-hetzner = certbot_dns_hetzner.dns_hetzner:Authenticator',
        ],
    },
    test_suite="certbot_dns_ispconfig",
)
