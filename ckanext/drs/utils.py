from typing import List, Dict  # noqa: F401

from ckan.plugins import toolkit as tk

import logging

log = logging.getLogger(__name__)


SUPPORTED_TYPES =  {
            'supported_types': List[str],
            'passport_auth_issuers': List[str],
            'bearer_auth_issuers': List[str]
        }
    

ATTRIBUTES_MAP = {
            'supported_types': 'supported_types',
            'passport_auth_issuers': 'passport_auth_issuers',
            'bearer_auth_issuers': 'bearer_auth_issuers'
        }