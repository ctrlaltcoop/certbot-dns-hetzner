"""
Fakes needed for tests
"""

FAKE_API_TOKEN = "XXXXXXXXXXXXXXXXXXXxxx"
FAKE_RECORD = {
    "record": {
        "id": "123Fake",
    }
}

FAKE_DOMAIN = "some.domain"
FAKE_ZONE_ID = "xyz"
FAKE_RECORD_ID = "zzz"
FAKE_RECORD_NAME = "thisisarecordname"

FAKE_RECORD_RESPONSE = {
    "record": {
        "id": FAKE_RECORD_ID,
        "name": "string",
    }
}

FAKE_RECORDS_RESPONSE_WITH_RECORD = {
    "records": [
        {
            "id": FAKE_RECORD_ID,
            "name": FAKE_RECORD_NAME,
        }
    ]
}

FAKE_RECORDS_RESPONSE_WITHOUT_RECORD = {
    "records": [
        {
            "id": "nottheoneuwant",
            "name": "string",
        }
    ]
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
