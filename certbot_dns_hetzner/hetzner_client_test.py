import unittest

import requests_mock
from requests import ConnectionError, ConnectTimeout

from certbot_dns_hetzner.hetzner_client import HETZNER_API_ENDPOINT, _ZoneNotFoundException, \
    _MalformedResponseException, _NotAuthorizedException

FAKE_API_TOKEN = 'XXXXXXXXXXXXXXXXXXXxxx'
FAKE_RECORD = {
    "record": {
        'id': "123Fake",
    }
}

FAKE_DOMAIN = 'some.domain'
FAKE_ZONE_ID = 'xyz'
FAKE_RECORD_ID = 'zzz'

FAKE_RECORD_RESPONSE = {
  "record": {
    "id": FAKE_RECORD_ID,
    "name": "string",
  }
}

FAKE_ZONES_RESPONSE_WITH_DOMAIN = {
  "zones": [
    {
      "id": FAKE_ZONE_ID,
      "name": FAKE_DOMAIN,
    }
  ]
}

FAKE_ZONES_RESPONSE_WITHOUT_DOMAIN = {
  "zones": [
    {
      "id": "string",
      "name": "string",
    }
  ]
}


class HetznerClientTest(unittest.TestCase):
    record_name = 'foo'
    record_content = 'bar'
    record_ttl = 42

    def setUp(self):
        from certbot_dns_hetzner.dns_hetzner import _HetznerClient
        self.client = _HetznerClient(FAKE_API_TOKEN)

    def test_add_record(self):
        with requests_mock.Mocker() as m:
            m.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_ZONES_RESPONSE_WITH_DOMAIN)
            m.post('{0}/records'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_RECORD_RESPONSE)
            response = self.client.add_record(FAKE_DOMAIN, "TXT", "somename", "somevalue", 42)
            self.assertEqual(response, FAKE_RECORD_RESPONSE)

    def test_add_record_but_zone_is_not_in_account(self):
        with requests_mock.Mocker() as m:
            m.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_ZONES_RESPONSE_WITHOUT_DOMAIN)
            m.post('{0}/records'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_RECORD_RESPONSE)
            self.assertRaises(
                _ZoneNotFoundException,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42
            )

    def test_add_record_but_record_creation_not_200(self):
        with requests_mock.Mocker() as m:
            m.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=200, json=FAKE_ZONES_RESPONSE_WITH_DOMAIN)
            m.post('{0}/records'.format(HETZNER_API_ENDPOINT), status_code=406)
            self.assertRaises(
                _MalformedResponseException,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42
            )

    def test_add_record_but_zone_listing_is_401(self):
        with requests_mock.Mocker() as m:
            m.get('{0}/zones'.format(HETZNER_API_ENDPOINT), status_code=401)
            m.post('{0}/records'.format(HETZNER_API_ENDPOINT), status_code=200)
            self.assertRaises(
                _NotAuthorizedException,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42
            )

    def test_add_record_but_zone_listing_times_out(self):
        with requests_mock.Mocker() as m:
            m.get('{0}/zones'.format(HETZNER_API_ENDPOINT), exc=ConnectTimeout)
            m.post('{0}/records'.format(HETZNER_API_ENDPOINT), status_code=200)
            self.assertRaises(
                ConnectionError,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42
            )

    def test_delete_record(self):
        with requests_mock.Mocker() as m:
            m.delete('{0}/records/{1}'.format(HETZNER_API_ENDPOINT, FAKE_RECORD_ID), status_code=200)
            self.client.delete_record(FAKE_RECORD_ID)

    def test_delete_but_authorization_fails(self):
        with requests_mock.Mocker() as m:
            m.delete('{0}/records/{1}'.format(HETZNER_API_ENDPOINT, FAKE_RECORD_ID), status_code=401)
            self.assertRaises(
                _NotAuthorizedException,
                self.client.delete_record, FAKE_RECORD_ID
            )

    def test_delete_record_but_deletion_is_404(self):
        with requests_mock.Mocker() as m:
            m.delete('{0}/records/{1}'.format(HETZNER_API_ENDPOINT, FAKE_RECORD_ID), status_code=404)
            self.assertRaises(
                _MalformedResponseException,
                self.client.delete_record, FAKE_RECORD_ID
            )

