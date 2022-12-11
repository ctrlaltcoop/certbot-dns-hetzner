"""DNS Authenticator for Hetzner DNS."""
import tldextract
from certbot.plugins import dns_common, dns_common_lexicon
from lexicon.providers import hetzner

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
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=60
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
        zone_name = tldextract.extract(domain)
        return '.'.join([zone_name.domain, zone_name.suffix])

    def _perform(self, domain, validation_name, validation):
        self._get_hetzner_client().add_txt_record(
            self._get_zone(domain),
            self._fqdn_format(validation_name),
            validation
        )

    def _cleanup(self, domain, validation_name, validation):
        self._get_hetzner_client().del_txt_record(
            self._get_zone(domain),
            self._fqdn_format(validation_name),
            validation
        )

    def _get_hetzner_client(self):
        return _HetznerClient(self.credentials.conf("api_token"))

    @staticmethod
    def _fqdn_format(name):
        if not name.endswith("."):
            return f"{name}."
        return name


class _HetznerClient(dns_common_lexicon.LexiconClient):
    """
    Encapsulates all communication with the Hetzner via Lexicon.
    """
    def __init__(self, auth_token):
        super().__init__()

        config = dns_common_lexicon.build_lexicon_config('hetzner', {
            'ttl': TTL,
        }, {
            'auth_token': auth_token,
        })

        self.provider = hetzner.Provider(config)
