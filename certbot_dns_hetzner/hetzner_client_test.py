# pylint: disable=W0212
"""
Test suite for _HetznerClient
"""
import unittest
import requests

import requests_mock

from certbot_dns_hetzner.fakes import FAKE_API_TOKEN, FAKE_RECORD_RESPONSE, FAKE_DOMAIN, \
    FAKE_ZONES_RESPONSE_WITH_DOMAIN, FAKE_ZONES_RESPONSE_WITHOUT_DOMAIN, FAKE_RECORD_ID, FAKE_ZONE_ID, \
    FAKE_RECORDS_RESPONSE_WITH_RECORD, FAKE_RECORD_NAME, FAKE_RECORDS_RESPONSE_WITHOUT_RECORD
from certbot_dns_hetzner.hetzner_client import HETZNER_API_ENDPOINT, _ZoneNotFoundException, \
    _MalformedResponseException, _NotAuthorizedException, _RecordNotFoundException


class HetznerClientTest(unittest.TestCase):
    record_name = 'foo'
    record_content = 'bar'
    record_ttl = 42

    def setUp(self):
        from certbot_dns_hetzner.dns_hetzner import _HetznerClient  # pylint: disable=import-outside-toplevel
        self.client = _HetznerClient(FAKE_API_TOKEN)

    def test_get_zone_by_name(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_ZONES_RESPONSE_WITH_DOMAIN)
            zone_id = self.client._get_zone_id_by_domain(FAKE_DOMAIN)
            self.assertEqual(zone_id, FAKE_ZONE_ID)

    def test_get_zone_by_name_but_zone_response_is_garbage(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, text='garbage')
            self.assertRaises(
                _MalformedResponseException,
                self.client._get_zone_id_by_domain, FAKE_DOMAIN
            )

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

    def test_add_record_but_record_but_unauthorized(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=401)
            self.assertRaises(
                _NotAuthorizedException,
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

    def test_delete_record_by_name_and_found(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_ZONES_RESPONSE_WITH_DOMAIN)
            mock.get('{0}/records?zone_id={1}'.format(
                HETZNER_API_ENDPOINT,
                FAKE_ZONE_ID
            ), status_code=200, json=FAKE_RECORDS_RESPONSE_WITH_RECORD)
            mock.delete('{0}/records/{1}'.format(HETZNER_API_ENDPOINT, FAKE_RECORD_ID), status_code=200)
            self.client.delete_record_by_name(FAKE_DOMAIN, FAKE_RECORD_NAME)

    def test_delete_record_by_name_but_its_not_found(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_ZONES_RESPONSE_WITH_DOMAIN)
            mock.get('{0}/records?zone_id={1}'.format(
                HETZNER_API_ENDPOINT,
                FAKE_ZONE_ID
            ), status_code=200, json=FAKE_RECORDS_RESPONSE_WITHOUT_RECORD)
            self.assertRaises(
                _RecordNotFoundException,
                self.client.delete_record_by_name, FAKE_DOMAIN, FAKE_RECORD_NAME
            )

    def test_delete_record_by_name_but_zone_is_not_found(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_ZONES_RESPONSE_WITHOUT_DOMAIN)
            self.assertRaises(
                _ZoneNotFoundException,
                self.client.delete_record_by_name, FAKE_DOMAIN, FAKE_RECORD_NAME
            )
