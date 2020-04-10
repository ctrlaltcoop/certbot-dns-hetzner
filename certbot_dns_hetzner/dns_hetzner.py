"""DNS Authenticator for Hetzner DNS."""
import logging

import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common
from requests import ConnectionError

from certbot_dns_hetzner.hetzner_client import \
    _MalformedResponseException, \
    _HetznerClient, \
    _ZoneNotFoundException, _NotAuthorizedException

logger = logging.getLogger(__name__)
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
                'api_token': 'Hetzner API Token from \'https://dns.hetzner.com/settings/api-token\'',
            }
        )

    def _perform(self, domain, validation_name, validation):
        try:
            record_response = self._get_hetzner_client().add_record(
                domain,
                "TXT",
                '{0}.'.format(validation_name),
                validation,
                TTL
            )
            self.record_id = record_response['record']['id']
        except (_ZoneNotFoundException, ConnectionError, _MalformedResponseException, _NotAuthorizedException) as e:
            raise errors.PluginError(e)

    def _cleanup(self, domain, validation_name, validation):
        try:
            if self.record_id:
                self._get_hetzner_client().delete_record(record_id=self.record_id)
        except (ConnectionError, _NotAuthorizedException) as e:
            raise errors.PluginError(e)

    def _get_hetzner_client(self):
        return _HetznerClient(
            self.credentials.conf('api_token'),
        )

