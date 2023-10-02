# endcoding: utf-8

import logging

from ckan.plugins import toolkit as tk

from ckanext.drs.utils import SUPPORTED_TYPES

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