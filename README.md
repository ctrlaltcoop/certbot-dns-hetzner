# Hetzner DNS Authenticator certbot plugin
[![codecov](https://codecov.io/gh/ctrlaltcoop/certbot-dns-hetzner/branch/main/graph/badge.svg?token=3XJVTPZ0AM)](https://codecov.io/gh/ctrlaltcoop/certbot-dns-hetzner)
![Tests, Coverage](https://github.com/ctrlaltcoop/certbot-dns-hetzner/workflows/Tests,%20Coverage/badge.svg?branch=main)
[![PyPI version](https://badge.fury.io/py/certbot-dns-hetzner.svg)](https://badge.fury.io/py/certbot-dns-hetzner)
![Supported Python](https://img.shields.io/pypi/pyversions/certbot-dns-hetzner)

This certbot plugin automates the process of
completing a dns-01 challenge by creating, and
subsequently removing, TXT records using the Hetzner DNS API.

## Requirements

### For certbot < 2

Notice that this plugin is only supporting certbot>=2.0 from 2.0 onwards. For older certbot versions use 1.x releases.

## Install

Install this package via pip in the same python environment where you installed your certbot.

```
pip install certbot-dns-hetzner
```

## Usage

To start using DNS authentication for the Hetzner DNS API, pass the following arguments on certbot's command line:

| Option                                                     | Description                                      |
|------------------------------------------------------------|--------------------------------------------------|
| `--authenticator dns-hetzner`                              | select the authenticator plugin (Required)       |
| `--dns-hetzner-credentials`                                | Hetzner DNS API credentials INI file. (Required) |
| `--dns-hetzner-propagation-seconds`                        | Seconds to wait for the TXT record to propagate  |

## Credentials


From the hetzner DNS control panel at https://dns.hetzner.com go to "API Tokens" and add a personal access token.  
Please make sure to use the absolute path - some users experienced problems with relative paths.  

An example ``credentials.ini`` file:

```ini
dns_hetzner_api_token = nohnah4zoo9Kiejee9aGh0thoopee2sa
```
## Examples
To acquire a certificate for `example.com`
```shell script
certbot certonly \\
 --authenticator dns-hetzner \\
 --dns-hetzner-credentials /path/to/my/hetzner.ini \\
 -d example.com
```

To acquire a certificate for ``*.example.com``
```shell script
   certbot certonly \\
     --authenticator dns-hetzner \\
     --dns-hetzner-credentials /path/to/my/hetzner.ini \\
     -d '*.example.com'
```
     
## Troubleshooting

### Plugin not showing up
If `certbot plugins` does not show the installed plugin, you might need to set `CERTBOT_PLUGIN_PATH`.  
```
CERTBOT_PLUGIN_PATH=/usr/local/lib/python3.9/site-packages/ certbot renew
```  
[See letsencrypt community thread](https://community.letsencrypt.org/t/how-do-i-make-certbot-find-use-an-installed-plugin/198647/5)

### Renewing certificate fails
Please ensure to use an absolute path for the credentials file - some users experienced problems with relative paths.

### Not working with snap
We did not nor plan to support snap - it was created from this [repo](https://github.com/BigMichi1/certbot-dns-hetzner).  
Feel free to start a new snap package yourself - we would happily link it here.

## Thanks to

Of course certbot, which examples and documentation I used to implement this plugin. And to https://github.com/m42e/certbot-dns-ispconfig which served as an excellent example and README template as well.

