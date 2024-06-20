"""DNS Authenticator for Hetzner DNS."""
import tldextract
from certbot.plugins import dns_common
from lexicon.client import Client
from lexicon.config import ConfigResolver

TTL = 60


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Hetzner
    This Authenticator uses the Hetzner DNS API to fulfill a dns-01 challenge.
    """

    description = (
        "Obtain certificates using a DNS TXT record (if you are using Hetzner for DNS)."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add, default_propagation_seconds = 60):
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=default_propagation_seconds
        )
        add("credentials", help="Hetzner credentials INI file.")

    def more_info(self):  # pylint: disable=missing-function-docstring
        return (
            "This plugin configures a DNS TXT record to respond to a dns-01 challenge using "
            + "the Hetzner API."
        )

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "Hetzner credentials INI file",
            {
                "api_token": "Hetzner API Token from 'https://dns.hetzner.com/settings/api-token'",
            },
        )

    @staticmethod
    def _get_zone(domain):
        extract = tldextract.TLDExtract()
        zone_name = extract(domain, include_psl_private_domains=True)
        return '.'.join([zone_name.domain, zone_name.suffix])

    def _perform(self, domain, validation_name, validation):
        with self._get_hetzner_client(domain) as client:
            client.create_record("TXT", self._fqdn_format(validation_name), validation)

    def _cleanup(self, domain, validation_name, validation):
        with self._get_hetzner_client(domain) as client:
            client.delete_record(None, "TXT", self._fqdn_format(validation_name), validation)

    def _get_hetzner_client(self, domain):
        config = ConfigResolver().with_env().with_dict({
            "provider_name": "hetzner",
            "hetzner": {
                "auth_token": self.credentials.conf("api_token")
            },

            "ttl": TTL,
            "domain": self._get_zone(domain),
        })
        return Client(config)

    @staticmethod
    def _fqdn_format(name):
        if not name.endswith("."):
            return f"{name}."
        return name
