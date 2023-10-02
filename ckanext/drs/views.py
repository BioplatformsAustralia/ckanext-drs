
import json
import requests

from flask import Blueprint
from ckan.views import api

from ckan.plugins import toolkit as tk

import logging


log = logging.getLogger(__name__)

drs_blueprint = Blueprint('drs', __name__, url_prefix='/drs')


def drs_option(res_id):
    # Return the DRS option for a resource
    response = tk.get_action('drs_option_show')(
        {'ignore_auth': True}, {'resource_id': res_id})

    return response
    
    

drs_blueprint.add_url_rule('/option/<res_id>', view_func=drs_option, methods=['OPTIONS'])
