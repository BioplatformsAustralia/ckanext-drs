
import json
import requests

from flask import Blueprint, make_response

from ckan.plugins import toolkit as tk

import logging


log = logging.getLogger(__name__)

drs_blueprint = Blueprint('drs', __name__, url_prefix='/drs')


def drs_option(res_id):
    # Return the DRS option for a resource
    response = tk.get_action('drs_option_show')(
        {'ignore_auth': True}, {'resource_id': res_id})

    return response


def service_info():
    # Return the DRS service info
    response = tk.get_action('drs_service_info_show')(
        {}, {})

    return make_response(str(response), 200, {'Content-Type': 'application/json'})
    
    

drs_blueprint.add_url_rule('/option/<res_id>', view_func=drs_option, methods=['OPTIONS'])
drs_blueprint.add_url_rule('/service-info', view_func=service_info, methods=['GET'])
