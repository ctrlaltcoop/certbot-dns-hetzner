"""
Test suite for _HetznerClient
"""
import unittest
import requests

import requests_mock

from certbot_dns_hetzner.fakes import FAKE_API_TOKEN, FAKE_RECORD_RESPONSE, FAKE_DOMAIN, \
    FAKE_ZONES_RESPONSE_WITH_DOMAIN, FAKE_ZONES_RESPONSE_WITHOUT_DOMAIN, FAKE_RECORD_ID
from certbot_dns_hetzner.hetzner_client import HETZNER_API_ENDPOINT, _ZoneNotFoundException, \
    _MalformedResponseException, _NotAuthorizedException


class HetznerClientTest(unittest.TestCase):
    record_name = 'foo'
    record_content = 'bar'
    record_ttl = 42

    def setUp(self):
        from certbot_dns_hetzner.dns_hetzner import _HetznerClient  # pylint: disable=import-outside-toplevel
        self.client = _HetznerClient(FAKE_API_TOKEN)

    def test_add_record(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_ZONES_RESPONSE_WITH_DOMAIN)
            mock.post('{0}/records'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_RECORD_RESPONSE)
            response = self.client.add_record(FAKE_DOMAIN, "TXT", "somename", "somevalue", 42)
            self.assertEqual(response, FAKE_RECORD_RESPONSE)

    def test_add_record_but_zone_is_not_in_account(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_ZONES_RESPONSE_WITHOUT_DOMAIN)
            mock.post('{0}/records'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_RECORD_RESPONSE)
            self.assertRaises(
                _ZoneNotFoundException,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42
            )

    def test_add_record_but_record_creation_not_200(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_ZONES_RESPONSE_WITH_DOMAIN)
            mock.post('{0}/records'.format(HETZNER_API_ENDPOINT), status_code=406)
            self.assertRaises(
                _MalformedResponseException,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42
            )

    def test_add_record_but_zone_listing_is_401(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=401)
            mock.post('{0}/records'.format(HETZNER_API_ENDPOINT), status_code=200)
            self.assertRaises(
                _NotAuthorizedException,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42
            )

    def test_add_record_but_zone_listing_times_out(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), exc=requests.ConnectTimeout)
            mock.post('{0}/records'.format(HETZNER_API_ENDPOINT), status_code=200)
            self.assertRaises(
                requests.ConnectionError,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42
            )

    def test_delete_record(self):
        with requests_mock.Mocker() as mock:
            mock.delete('{0}/records/{1}'.format(HETZNER_API_ENDPOINT, FAKE_RECORD_ID), status_code=200)
            self.client.delete_record(FAKE_RECORD_ID)

    def test_delete_but_authorization_fails(self):
        with requests_mock.Mocker() as mock:
            mock.delete('{0}/records/{1}'.format(HETZNER_API_ENDPOINT, FAKE_RECORD_ID), status_code=401)
            self.assertRaises(
                _NotAuthorizedException,
                self.client.delete_record, FAKE_RECORD_ID
            )

    def test_delete_record_but_deletion_is_404(self):
        with requests_mock.Mocker() as mock:
            mock.delete('{0}/records/{1}'.format(HETZNER_API_ENDPOINT, FAKE_RECORD_ID), status_code=404)
            self.assertRaises(
                _MalformedResponseException,
                self.client.delete_record, FAKE_RECORD_ID
            )
