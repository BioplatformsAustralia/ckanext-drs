# endcoding: utf-8

import logging
from datetime import datetime

from ckan.plugins import toolkit as tk

from ckanext.drs.utils import SUPPORTED_TYPES

from ckanext.drs.models.get_service_info200_response import GetServiceInfo200Response
from ckanext.drs.models.drs_service_type import DrsServiceType
from ckanext.drs.models.service_organization import ServiceOrganization

log = logging.getLogger(__name__)


def option_show(contect , data_dict):
    obj_id = data_dict.get('object_id')
    # Return the DRS option for a resource
    if not obj_id:
        raise tk.ValidationError({'object_id': 'Missing object id'})
    response = {
        'supported_types': ['None'],
        'passport_auth_issuers': ["string"],
        'bearer_auth_issuers': ["string"]
    }
    bearer_auth_issuers = None
    supported_types = None
    try:
        if obj_id.startswith('~'):
            obj_id = obj_id[1:]
            package_dict = tk.get_action('package_show')({},{'id': obj_id})
            if package_dict.get('resource_premissions') != 'public':
                supported_types = ["BearerAuth"]
                bearer_auth_issuers = ["data.bpa.test.biocommons.org.au"]
            else:
                supported_types = ["None"]
        else:
            resource_dict = tk.get_action('resource_show')({},{'id': obj_id})
            supported_types = ["None"]  
    except tk.ObjectNotFound:
        tk.abort(404, tk._('Resource not found'))
    except tk.NotAuthorized:
        supported_types = ["BearerAuth"]
        bearer_auth_issuers = ["data.bpa.test.biocommons.org.au"]
    if bearer_auth_issuers:
        response.update({'bearer_auth_issuers': bearer_auth_issuers})
    response.update({'supported_types': supported_types})
    return response


def get_object_info(context, data_dict):
    # Return the DRS object info for a resource
    obj_id = data_dict.get('object_id')
    is_resource = False
    if obj_id.startswith('~'):
        obj_id = obj_id[1:]
        result_dict = tk.get_action('package_show')({},{'id': obj_id})
    else:
        result_dict = tk.get_action('resource_show')({},{'id': obj_id})
        is_resource = True

    result = _extract_drs_object(result_dict, is_resource=is_resource)

    return result



def service_info_show(context, data_dict):
    response = {
        'contact_url': 'mailto:uwe@biocommons.org.au',
        'created_at': datetime(2023, 3, 1, 0, 0).date(),
        'description': 'This service wraps around the CKAN API of BPA data portal. A '
                        'CKAN api key can be provided as a Bearer Token',
        'documentation_url': None,
        'environment': 'dev',
        'id': {'artifact': 'drs'},
        'name': 'com.bioplatforms.data',
        'organization': {'name': 'Bioplatforms Australia',
                        'url': 'https://data.bioplatforms.com'},
        'type': 'Bioplatforms Australia Data Portal DRS service',
        'updated_at': datetime(2023, 3, 9, 0, 0).date(),
        'version': '0.5b'
    }
    
    
    return response

def _extract_drs_object(data_dict, is_resource=True):
    '''{
        "id": "b8cd0667-2c33-4c9f-967b-161b905932c9",
        "description": "Open dataset of 384 phenopackets",
        "created_time": "2021-03-12T20:00:00Z",
        "name": "phenopackets.test.dataset",
        "size": 143601,
        "updated_time": "2021-03-13T12:30:45Z",
        "version": "1.0.0",
        "self_uri": "drs://localhost:4500/b8cd0667-2c33-4c9f-967b-161b905932c9",
        "contents": [
            {
                "name": "phenopackets.mundhofir.family",
                "drs_uri": [
                    "drs://localhost:4500/1af5cdcf-898c-4dbc-944e-1ac95e82c0ea"
                ],
                "id": "1af5cdcf-898c-4dbc-944e-1ac95e82c0ea"
            },
            {
                "name": "phenopackets.zhang.family",
                "drs_uri": [
                    "drs://localhost:4500/355a74bd-6571-4d4a-8602-a9989936717f"
                ],
                "id": "355a74bd-6571-4d4a-8602-a9989936717f"
            },
            {
                "name": "phenopackets.cao.family",
                "drs_uri": [
                    "drs://localhost:4500/a1dd4ae2-8d26-43b0-a199-342b64c7dff6"
                ],
                "id": "a1dd4ae2-8d26-43b0-a199-342b64c7dff6"
            },
            {
                "name": "phenopackets.lalani.family",
                "drs_uri": [
                    "drs://localhost:4500/c69a3d6c-4a28-4b7c-b215-0782f8d62429"
                ],
                "id": "c69a3d6c-4a28-4b7c-b215-0782f8d62429"
            }
        ]

    }
    '''
    drs_object = {
        'id': data_dict.get('id'),
        'name': (data_dict.get('filename') if is_resource else data_dict.get('name')) or "",
        'description': data_dict.get('description') or "",
        'created_time': data_dict.get('created') if is_resource else data_dict.get('metadata_created'),
        'updated_time': data_dict.get('last_modified') if is_resource else data_dict.get('metadata_modified'),
        'size': data_dict.get('size') if is_resource else 0,
        'version': data_dict.get('version') if is_resource and data_dict.get('version') else 1,
        'self_uri': f'drs://{data_dict.get("url").split("/")[2]}/{data_dict.get("id")}',
        'contents': [
            {
                'name': data_dict.get('name'),
                'drs_uri': [f'drs://{data_dict.get("url").split("/")[2]}/{data_dict.get("id")}'],
                'id': data_dict.get('id')
            }
        ]
    }
    return drs_object