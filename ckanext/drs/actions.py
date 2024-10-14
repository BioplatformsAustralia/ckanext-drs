# endcoding: utf-8

import logging
import functools
from datetime import datetime
from urllib.parse import urlparse

from ckan.plugins import toolkit as tk

log = logging.getLogger(__name__)


def option_show(context, data_dict):
    log.info("***************** OPTION SHOW" + data_dict)
    obj_id = data_dict.get("object_id")
    # Return the DRS option for a resource
    if not obj_id:
        raise tk.ValidationError({"object_id": "Missing object id"})
    response = {
        "supported_types": ["None"],
        "passport_auth_issuers": ["string"],
        "bearer_auth_issuers": ["string"],
    }
    bearer_auth_issuers = None
    supported_types = None
    try:
        if obj_id.startswith("~"):
            obj_id = obj_id[1:]
            package_dict = tk.get_action("package_show")(
                {"ignore_auth": True}, {"id": obj_id}
            )
            if package_dict.get("resource_premissions") != "public":
                supported_types = ["BearerAuth"]
                bearer_auth_issuers = ["data.bpa.test.biocommons.org.au"]
            else:
                supported_types = ["None"]
        else:
            resource_dict = tk.get_action("resource_show")(
                {"ignore_auth": True}, {"id": obj_id}
            )
            log.info(resource_dict)
            supported_types = ["None"]
    except tk.ObjectNotFound:
        tk.abort(404, tk._("Resource not found"))
    except tk.NotAuthorized:
        supported_types = ["BearerAuth"]
        bearer_auth_issuers = ["data.bpa.test.biocommons.org.au"]
    if bearer_auth_issuers:
        response.update({"bearer_auth_issuers": bearer_auth_issuers})
    response.update({"supported_types": supported_types})
    return response


def get_object_info(context, data_dict):
    log.info(data_dict)
    # Return the DRS object info for a resource
    obj_id = data_dict.get("object_id")
    is_resource = False
    if obj_id.startswith("~"):
        obj_id = obj_id[1:]
        result_dict = tk.get_action("package_show")(
            {"ignore_auth": True}, {"id": obj_id}
        )
    else:
        result_dict = tk.get_action("resource_show")(
            {"ignore_auth": True}, {"id": obj_id}
        )
        is_resource = True

    result = _extract_drs_object(result_dict, is_resource=is_resource)

    return result


def service_info_show(context, data_dict):
    response = {
        "contact_url": "mailto:uwe@biocommons.org.au",
        "created_at": datetime(2023, 3, 1, 0, 0).date(),
        "description": "This service wraps around the CKAN API of BPA data portal. A "
        "CKAN api key can be provided as a Bearer Token",
        "documentation_url": None,
        "environment": "dev",
        "id": {"artifact": "drs"},
        "name": "com.bioplatforms.data",
        "organization": {
            "name": "Bioplatforms Australia",
            "url": "https://data.bioplatforms.com",
        },
        "type": "Bioplatforms Australia Data Portal DRS service",
        "updated_at": datetime(2023, 3, 9, 0, 0).date(),
        "version": "0.5b",
    }
    return response


def _extract_drs_contents_object(resource, drs_host=None):
    drs_uri = f'drs://{drs_host}/{resource.get("id")}'
    contents_object = {
        "name": resource.get("name"),
        "id": resource.get("id"),
        "drs_uri": [drs_uri],
    }

    return contents_object


def _extract_drs_object(data_dict, is_resource=True):
    drs_host = urlparse(tk.config.get("ckan.site_url")).hostname
    drs_uri = f'drs://{drs_host}/{data_dict.get("id")}' if is_resource else None
    drs_object = {
        "id": data_dict.get("id"),
        "name": (data_dict.get("filename") if is_resource else data_dict.get("name"))
        or "",
        "description": data_dict.get("description") or "",
        "created_time": (
            data_dict.get("created")
            if is_resource
            else data_dict.get("metadata_created")
        ),
        "updated_time": (
            data_dict.get("last_modified")
            if is_resource
            else data_dict.get("metadata_modified")
        ),
        "size": data_dict.get("size") if is_resource else 0,
        "version": (
            data_dict.get("version") if is_resource and data_dict.get("version") else 1
        ),
        "self_uri": drs_uri,
        "contents": [
            {
                "name": data_dict.get("name"),
                "drs_uri": [drs_uri],
                "id": data_dict.get("id"),
            }
        ],
    }
    if is_resource:
        drs_object.update(
            {
                "mime_type": data_dict.get("mimetype"),
                "checksums": [{"checksum": data_dict.get("md5"), "type": "md5"}],
                "access_methods": [
                    {
                        "access_id": "download_window",
                        "type": "https",
                    }
                ],
                "aliases": [data_dict.get("name")],
                "contents": [
                    {
                        "name": data_dict.get("name"),
                        "drs_uri": [drs_uri],
                        "id": data_dict.get("id"),
                    }
                ],
                "size": data_dict.get("size"),
                "version": data_dict.get("version") if data_dict.get("version") else 1,
            }
        )
    else:
        # Return a bundle of ContentsObjects
        contents = list(
            map(
                functools.partial(_extract_drs_contents_object, drs_host=drs_host),
                data_dict.get("resources"),
            )
        )
        drs_object.update(
            {
                "mime_type": None,
                "checksums": [{"checksum": None, "type": None}],
                "aliases": [data_dict.get("name")],
                "contents": contents,
                "checksum": None,
                "size": 0,
                "version": 1,
            }
        )
    return drs_object


@tk.side_effect_free
def drs_get_access_url(context, data_dict):
    object_id = data_dict.get("object_id", None)
    access_id = data_dict.get("access_id", None)
    if access_id != "download_window":
        raise tk.ValidationError({"access_id": "Unsupported access id"})

    res_data = tk.get_action("resource_show")(
            {"ignore_auth": True}, {"id": object_id}
    )

    package_id = res_data.get("package_id")
    resource_id = data_dict.get("object_id", None)

    # Return S3 download link for a resource
    dw_data_dict = {"package_id": package_id, "resource_id": resource_id}
    res_data = tk.get_action("download_window")(context, dw_data_dict)
    link = res_data.get("url")

    # Return AccessURL object
    response = {"url": link}
    return response
