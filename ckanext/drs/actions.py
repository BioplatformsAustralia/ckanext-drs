# endcoding: utf-8

import logging
from datetime import datetime

from ckan.plugins import toolkit as tk

from ckanext.drs.utils import SUPPORTED_TYPES

from ckanext.drs.models.get_service_info200_response import GetServiceInfo200Response
from ckanext.drs.models.drs_service_type import DrsServiceType
from ckanext.drs.models.service_organization import ServiceOrganization

log = logging.getLogger(__name__)


def drs_option_show(res_id):
    # Return the DRS option for a resource
    if not res_id:
        raise tk.ValidationError({'resource_id': 'Missing resource_id'})
    response = {
        'supported_types': ['None'],
        'passport_auth_issuers': ["string"],
        'bearer_auth_issuers': ["string"]
    }
    supported_types = None
    try:
        if res_id.startswith('~'):
            res_id = res_id[1:]
            package_dict = tk.get_action('package_show')({},{'id': res_id})
            if package_dict.get('resource_premissions') != 'public':
                supported_types = ["BearerAuth"]
                bearer_auth_issuers = ["data.bpa.test.biocommons.org.au"]
            else:
                supported_types = ["None"]
        else:
            resource_dict = tk.get_action('resource_show')({},{'id': res_id})
            supported_types = ["None"]  
    except tk.ObjectNotFound:
        tk.abort(404, tk._('Resource not found'))
    except tk.NotAuthorized:
        supported_types = ["BearerAuth"]
        bearer_auth_issuers = ["data.bpa.test.biocommons.org.au"]
    response.update({'supported_types': supported_types, 'bearer_auth_issuers': bearer_auth_issuers})
    return response


def service_info_show(context, data_dict):
    # Return the DRS service info
    service_type = DrsServiceType("drs")
    service_org = ServiceOrganization("Bioplatforms Australia", "https://data.bioplatforms.com")
    response = GetServiceInfo200Response(
        service_type,
        "com.bioplatforms.data",
        "Bioplatforms Australia Data Portal DRS service",
        "This service wraps around the CKAN API of BPA data portal. A CKAN api key can be provided as a Bearer Token",
        service_org, "mailto:uwe@biocommons.org.au",
        None,
        datetime(2023, 3, 1, 0, 0, 0, 0),
        datetime(2023, 3, 9, 0, 0, 0, 0),
        "dev",
        "0.5b")
    return response