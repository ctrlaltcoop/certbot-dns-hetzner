import sys

from setuptools import find_packages
from setuptools import setup

version = '0.1.0.dev0'


install_requires = [
    'certbot>=1.1.0',
    'requests>=2.23.0',
    'setuptools',
    'zope.interface',
]

setup(
    name='certbot-dns-hetzner',
    version=version,
    description="Hetzner DNS Authenticator plugin for Certbot",
    url='https://github.com/ctrlaltcoop/certbot-dns-hetzner',
    author="ctrl.alt.coop",
    author_email='kontakt@ctrl.alt.coop',
    license='Apache License 2.0',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
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
        'Programming Language :: Python :: 3.5',
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
)
