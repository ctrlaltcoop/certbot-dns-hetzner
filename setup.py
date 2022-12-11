import os

from setuptools import find_packages
from setuptools import setup

version = '2.0.0'

# This package relies on PyOpenSSL, requests, and six, however, it isn't
# specified here to avoid masking the more specific request requirements in
# acme. See https://github.com/pypa/pip/issues/988 for more info.
install_requires = [
    'certbot>=2.0.0',
    'setuptools',
    'requests',
    'requests-mock',
    'dns-lexicon>=3.11.6',
    'parsedatetime<=2.5;python_version<"3.0"'
]

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
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
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
    test_suite="certbot_dns_hetzner",
)
