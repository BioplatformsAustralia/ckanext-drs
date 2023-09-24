import json
import requests

from ckan.plugins import toolkit as tk

import logging

log = logging.getLogger(__name__)


def get_drs_resource(resource_dict):
    # check for drs resource
    drs_res = None
    user = tk.g.user
    if not user:
        raise tk.NotAuthorized
    
    tokens = tk.get_action(u"api_token_list")(
                {u"ignore_auth": True}, {u"user": user.get("name")})
    if not tokens:
        raise tk.NotAuthorized
    
    for token in tokens:
        if token["name"] == "drs":
            drs_res = token["token"]
            break
    if token is None:
        raise tk.NotAuthorized
    
    # get drs resource
    drs_url = tk.config.get("ckanext.drs.url")
    if not drs_url:
        raise tk.NotAuthorized
    
    

def drs_option(res_id):
    drs_object = requests.options(
        url="https://{serverURL}/ga4gh/drs/v1/objects/{object_id}".format(
            serverURL=tk.config.get("ckanext.drs.url"),
            object_id=res_id
        ))
    
    if drs_object.status_code == 200:
        log.info("drs_object: {}".format(drs_object.content))
        return json.loads(drs_object.content)
    else:
        return None
    
def drs_object(res_id):
    drs_object = requests.get(
        url="https://{serverURL}/ga4gh/drs/v1/objects/{object_id}".format(
            serverURL=tk.config.get("ckanext.drs.url"),
            object_id=res_id
        ),
        headers={
            "Authorization": "Bearer {}".format(drs_option(res_id)["access_methods"][0]["access_id"])
        })
    
    if drs_object.status_code == 200:
        log.info("drs_object: {}".format(drs_object.content))
        return json.loads(drs_object.content)
    else:
        return None
    
def drs_object_url(res_id):
    '''
    Get info about a DrsObject through POST'ing a Passport. 
    '''
    drs_object = requests.post(
        url="https://{serverURL}/ga4gh/drs/v1/objects/{object_id}".format(
            serverURL=tk.config.get("ckanext.drs.url"),
            object_id=res_id
        ),
        headers={
            "Authorization": "Bearer {}".format(drs_option(res_id)["access_methods"][0]["access_id"])
        },
        json={
            "access_id": drs_option(res_id)["access_methods"][0]["access_id"],
            "access_url": drs_option(res_id)["access_methods"][0]["access_url"],
            "checksums": drs_option(res_id)["checksums"],
            "contents": drs_option(res_id)["contents"],
            "created_time": drs_option(res_id)["created_time"],
            "description": drs_option(res_id)["description"],
            "id": drs_option(res_id)["id"],
            "mime_type": drs_option(res_id)["mime_type"],
            "name": drs_option(res_id)["name"],
            "self_uri": drs_option(res_id)["self_uri"],
            "size": drs_option(res_id)["size"],
            "updated_time": drs_option(res_id)["updated_time"],
            "version": drs_option(res_id)["version"]
        })
    
