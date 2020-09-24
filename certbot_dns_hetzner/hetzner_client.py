"""
A Hetzner helper class to wrap the API relevant for the functionality in this plugin
"""
import json
import requests

from certbot.plugins import dns_common

HETZNER_API_ENDPOINT = 'https://dns.hetzner.com/api/v1'


class _HetznerException(Exception):
    pass


class _ZoneNotFoundException(_HetznerException):
    def __init__(self, domain_name, *args):
        super(_ZoneNotFoundException, self).__init__('Zone {0} not found in Hetzner account'.format(domain_name), *args)
        self.domain_name = domain_name


class _MalformedResponseException(_HetznerException):
    def __init__(self, cause, *args):
        super(_MalformedResponseException, self).__init__(
            'Received an unexpected response from Hetzner API:\n{0}'.format(cause), *args)
        self.cause = cause


class _RecordNotFoundException(_HetznerException):
    def __init__(self, record_name, *args):
        super(_RecordNotFoundException, self).__init__('Record with name {0} not found'.format(record_name), *args)
        self.record_name = record_name


class _NotAuthorizedException(_HetznerException):
    def __init__(self, *args):
        super(_NotAuthorizedException, self).__init__('Malformed authorization or invalid API token', *args)


class _UnprocessableEntityException(_HetznerException):
    def __init__(self, record_data, *args):
        super(_UnprocessableEntityException, self).__init__('Unprocessable entity in record {0}'.format(record_data),
                                                            *args)
        self.record_data = record_data


class _HetznerClient:
    """
    A little helper class for operations on the Hetzner DNS API
    """

    def __init__(self, token):
        """
        Initialize client by providing a Hetzner DNS API token
        :param token: Hetzner DNS API Token retrieved from: https://dns.hetzner.com/settings/api-token
        """
        self.token = token

    @property
    def _headers(self):
        return {
            "Content-Type": "application/json",
            "X-Consumer-Username": "",
            "Auth-API-Token": self.token,
        }

    def add_record(self, domain, record_type, name, value, ttl):  # pylint: disable=too-many-arguments
        """
        API call to add record to zone matching ``domain`` to your Hetzner Account, while specifying ``record_type``,
        ``name``, ``value`` and ``ttl``
        :param domain: Domain to determine zone where record should be added
        :param record_type: A valid DNS record type
        :param name: Full record name
        :param value: Record value
        :param ttl: Time to live
        :raises ._MalformedResponseException: If the response is missing expected values or is invalid JSON
        :raises ._ZoneNotFoundException: If no zone with the SLD and TLD of ``domain`` is found in your Hetzner account
        :raises ._NotAuthorizedException: If Hetzner does not accept the authorization credentials
        :raises ._UnprocessableEntityException: If the request is valid but still cannot be processed. e.g.
                                                if it's committed to the wrong zone
        :raises requests.exceptions.ConnectionError: If the API request fails
        """
        zone_id = self._get_zone_id_by_domain(domain)
        record_data = json.dumps({
            "value": value,
            "ttl": ttl,
            "type": record_type,
            "name": name,
            "zone_id": zone_id
        })
        create_record_response = requests.post(
            url="{0}/records".format(HETZNER_API_ENDPOINT),
            headers=self._headers,
            data=record_data
        )
        if create_record_response.status_code == 401:
            raise _NotAuthorizedException()
        if create_record_response.status_code == 422:
            raise _UnprocessableEntityException(record_data)
        try:
            return create_record_response.json()
        except (ValueError, UnicodeDecodeError) as exception:
            raise _MalformedResponseException(exception)

    def delete_record_by_name(self, domain, record_name):
        """
        Searches for a zone matching ``domain``, if found find and delete a record matching ``record_name`
        Deletes record with ``record_id`` from your Hetzner Account
        :param domain: Domain of zone in which the record should be found
        :param record_name: ID of record to be deleted
        :raises requests.exceptions.ConnectionError: If the API request fails
        :raises ._MalformedResponseException: If the API response is not 200
        :raises ._ZoneNotFoundException: If no zone is found matching ``domain``
        :raises ._RecordNotFoundException: If no record is found matching ``record_name``
        :raises ._NotAuthorizedException: If Hetzner does not accept the authorization credentials
        """
        zone_id = self._get_zone_id_by_domain(domain)
        record_id = self._get_record_id_by_name(zone_id, record_name)
        self.delete_record(record_id)

    def delete_record(self, record_id):
        """
        Deletes record with ``record_id`` from your Hetzner Account
        :param record_id: ID of record to be deleted
        :raises requests.exceptions.ConnectionError: If the API request fails
        :raises ._MalformedResponseException: If the API response is not 200
        :raises ._NotAuthorizedException: If Hetzner does not accept the authorization credentials
        """
        response = requests.delete(
            url="{0}/records/{1}".format(HETZNER_API_ENDPOINT, record_id),
            headers=self._headers
        )
        if response.status_code == 401:
            raise _NotAuthorizedException()
        if response.status_code != 200:
            raise _MalformedResponseException('Status code not 200')

    def _get_record_id_by_name(self, zone_id, record_name):
        """
        :param zone_id: ID of dns zone where the record should be searched
        :param record_name: Name of the record that is searched
        :return: The ID of the record with name ``record_name`` if found
        :raises ._MalformedResponseException: If the response is missing expected values or is invalid JSON
        :raises requests.exceptions.ConnectionError: If the API request fails
        :raises ._NotAuthorizedException: If Hetzner does not accept the authorization credentials
        :rtype: str
        """
        records_response = requests.get(
            url="{0}/records".format(HETZNER_API_ENDPOINT),
            params={
                'zone_id': zone_id,
            },
            headers=self._headers
        )
        if records_response.status_code == 401:
            raise _NotAuthorizedException()
        try:
            records = records_response.json()['records']
            for record in records:
                if record['name'] == record_name:
                    return record['id']
        except (ValueError, UnicodeDecodeError, KeyError) as exception:
            raise _MalformedResponseException(exception)
        raise _RecordNotFoundException(record_name)

    def _get_zone_id_by_domain(self, domain):
        """
        Requests all dns zones from your Hetzner account and searches for a specific one to determine the ID of it
        :param domain: Name of dns zone where the record should be searched
        :return: The ID of the zone that is SLD and TLD of ``domain`` - if found
        :raises ._MalformedResponseException: If the response is missing expected values or is invalid JSON
        :raises ._ZoneNotFoundException: If no zone with the SLD and TLD of ``domain`` is found in your Hetzner account
        :raises ._NotAuthorizedException: If Hetzner does not accept the authorization credentials
        :raises requests.exceptions.ConnectionError: If the API request fails
        :rtype: str
        """
        domain_name_guesses = dns_common.base_domain_name_guesses(domain)
        zones_response = requests.get(
            url="{0}/zones".format(HETZNER_API_ENDPOINT),
            headers=self._headers,
        )
        if zones_response.status_code == 401:
            raise _NotAuthorizedException()
        try:
            zones = zones_response.json()['zones']
            # Find the most specific domain listed in the available zones
            for guess in domain_name_guesses:
                for zone in zones:
                    if zone['name'] == guess:
                        return zone['id']
        except (KeyError, UnicodeDecodeError, ValueError) as exception:
            raise _MalformedResponseException(exception)
        raise _ZoneNotFoundException(domain)
