"""DNS Authenticator for Hetzner DNS."""
import logging
import requests
import json

import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)

TOKEN_URL = 'https://dns.hetzner.com/settings/api-token'
HETZNER_API_ENDPOINT = 'https://dns.hetzner.com/api/v1'
TTL = 60


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Hetzner
    This Authenticator uses the Hetzner DNS API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using Hetzner for DNS).'
    record_id = None

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=60)
        add('credentials', help='Hetzner credentials INI file.')

    def more_info(self):  # pylint: disable=missing-function-docstring
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the Hetzner API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'Hetzner credentials INI file',
            {
                'api_token': 'Hetzner API Token from {0}'.format(TOKEN_URL),
            }
        )

    def _perform(self, domain, validation_name, validation):
        self.record_id = self._get_hetzner_client().add_record(domain, "TXT", '{0}.'.format(validation_name), validation)['record']['id']

    def _cleanup(self, domain, validation_name, validation):
        if self.record_id:
            self._get_hetzner_client().delete_record(record_id=self.record_id)

    def _get_hetzner_client(self):
        return _HetznerClient(
            self.credentials.conf('api_token'),
        )


class _HetznerClient:
    """
    A little helper class for operations on the Hetzner DNS API
    """

    def __init__(self, token):
        self.token = token

    @property
    def _headers(self):
        return {
            "Content-Type": "application/json",
            "X-Consumer-Username": "",
            "Auth-API-Token": self.token,
        }

    def add_record(self, domain, record_type, validation_name, validation):
        zone_id = self._get_zone_id_by_domain(domain)
        create_record_response = requests.post(
            url="{0}/records".format(HETZNER_API_ENDPOINT),
            headers=self._headers,
            data=json.dumps({
                "value": validation,
                "ttl": TTL,
                "type": record_type,
                "name": validation_name,
                "zone_id": zone_id
            })
        )
        return create_record_response.json()

    def delete_record(self, record_id):
        requests.delete(
            url="{0}/records/{1}".format(HETZNER_API_ENDPOINT, record_id),
            headers=self._headers
        )

    def _get_record_id_by_name(self, zone_id, record_name):
        records_response = requests.get(
            url="{0}/records".format(HETZNER_API_ENDPOINT),
            params={
                'zone_id': zone_id,
            },
            headers=self._headers
        )
        hint = None
        error = None

        records = records_response.json()['records']
        for record in records:
            if record['name'] == record_name:
                return record['id']
        hint = 'No record with name {0} found during cleanup'.format(record_name)
        raise errors.PluginError('Error deleting record for cleanup: {0}\n{1}\n{2}'
                                 .format(record_name, error if error else '', ' ({0})'.format(hint) if hint else ''))

    def _get_zone_id_by_domain(self, domain):
        domain_tokens = domain.split('.')
        hint = None
        error = None
        zones_response = requests.get(
            url="{0}/zones".format(HETZNER_API_ENDPOINT),
            headers=self._headers,
        )
        try:
            zones = zones_response.json()['zones']
            for zone in zones:
                zone_name_tokens = zone['name'].split('.')
                if zone_name_tokens[-1] == domain_tokens[-1] and zone_name_tokens[-2] == domain_tokens[-2]:
                    return zone['id']
            hint = "No zone found matching {0}".format(domain)
        except AttributeError as e:
            error = e
            hint = "Malformed response\n{0}".format(e)
        raise errors.PluginError('Error determining zone identifier for {0}: {1}.{2}'
                                 .format(domain, error if error else '', ' ({0})'.format(hint) if hint else ''))
