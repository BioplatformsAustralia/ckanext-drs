import logging

from ckan.plugins import toolkit as tk

logger = logging.getLogger(__name__)


def option_show(context, data_dict):
    '''
    Return the DRS option for a resource
    '''
    return {"success": True}


def service_info_show(context, data_dict):
    '''
    Return the DRS service info for a resource
    '''
    return {"success": True}


def get_object_info(context, data_dict):
    '''
    Check if the user has access to the object
    '''
    obj_id = data_dict.get("object_id")
    if obj_id.startswith("~"):
        obj_id = obj_id[1:]
        try:
            tk.check_access("package_show", context, {"id": obj_id})
            return {"success": True}
        except tk.NotAuthorized:
            return {"success": False}
    else:
        try:
            tk.check_access("resource_show", context, {"id": obj_id})
            return {"success": True}
        except tk.NotAuthorized:
            return {"success": False}


def drs_get_access_url(context, data_dict):
    # Authorization is enforced inside the action after the package_id is
    # resolved (it is not available in the data_dict at auth-check time).
    # The downstream `download_window` action performs the real auth check.
    return {"success": True}
