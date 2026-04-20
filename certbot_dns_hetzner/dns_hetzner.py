"""DNS Authenticator for Hetzner DNS."""

import tldextract
from certbot.errors import PluginError
from certbot.plugins import dns_common
from hcloud import Client, APIException
from hcloud.zones import Zone, ZoneRecord, ZoneRRSet

_TLD_EXTRACT = tldextract.TLDExtract(include_psl_private_domains=True)


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Hetzner
    This Authenticator uses the Hetzner DNS API to fulfill a dns-01 challenge.
    """

    description = "Obtain certificates using a DNS TXT record (if you are using Hetzner for DNS)."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add, default_propagation_seconds=60):
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=default_propagation_seconds)
        add("credentials", help="Hetzner credentials INI file.")

    def more_info(self):  # pylint: disable=missing-function-docstring
        return "This plugin configures a DNS TXT record to respond to a dns-01 challenge using the Hetzner API."

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "Hetzner credentials INI file",
            {
                "api_token": "Hetzner Cloud API Token from 'https://console.hetzner.com/projects/{id}/security/tokens'",
            },
        )

    @staticmethod
    def _get_zone(domain):
        """Extract the zone (registrable domain) from a given domain name."""
        zone_name = _TLD_EXTRACT(domain)

        if not zone_name.domain or not zone_name.suffix:
            raise PluginError(
                f"Could not extract valid zone from domain={domain!r}. "
                f"Ensure the domain is a valid FQDN."
            )

        return ".".join([zone_name.domain, zone_name.suffix])

    @staticmethod
    def _get_relative_name(validation_name, zone_name):
        """Strips the zone name from the FQDN to get the relative record name."""
        if validation_name == zone_name:
            return "@"
        if validation_name.endswith("." + zone_name):
            return validation_name[: -(len("." + zone_name))]
        return validation_name

    def _perform(self, domain, validation_name, validation):
        client = self._get_hetzner_client()
        zone_name = self._get_zone(domain)
        try:
            action = client.zones.add_rrset_records(
                rrset=ZoneRRSet(
                    zone=Zone(name=zone_name),
                    name=self._get_relative_name(validation_name, zone_name),
                    type="TXT",
                ),
                ttl=60,
                records=[ZoneRecord(value=f'"{validation}"')],
            )
            action.wait_until_finished()
        except APIException as apiException:
            raise PluginError(apiException)

    def _cleanup(self, domain, validation_name, validation):
        client = self._get_hetzner_client()
        zone_name = self._get_zone(domain)
        action = client.zones.remove_rrset_records(
            rrset=ZoneRRSet(
                zone=Zone(name=zone_name),
                name=self._get_relative_name(validation_name, zone_name),
                type="TXT",
            ),
            records=[ZoneRecord(value=f'"{validation}"')],
        )
        action.wait_until_finished()

    def _get_hetzner_client(self):
        return Client(token=self.credentials.conf("api_token"))
