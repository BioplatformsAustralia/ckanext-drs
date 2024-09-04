from flask import Blueprint

from ckan.plugins import toolkit as tk

import ckan.views.api as api
import logging


log = logging.getLogger(__name__)

drs_blueprint = Blueprint("drs", __name__, url_prefix="/ga4gh/drs/v1")


def drs_option(object_id):
    # Return the DRS option for a resource
    log.info("***************** OBJECT ID" + object_id)

    response = tk.get_action("drs_option_show")({}, {"object_id": object_id})

    return response


def drs_get_object_info(object_id):
    # Return the DRS object info for a resource
    response = tk.get_action("drs_get_object_info")({}, {"object_id": object_id})

    return response
    # return make_response(str(response), 200, {'Content-Type': 'application/json'})


def drs_get_access_url(object_id, access_id):
    # Return the DRS access url for a resource
    response = tk.get_action("drs_download_window")(
        {}, {"access_id": access_id, "object_id": object_id}
    )
    return response


def service_info():
    # Return the DRS service info
    result = tk.get_action("drs_service_info_show")({}, {})

    response = api._finish_ok(result, content_type="json")
    return response


drs_blueprint.add_url_rule(
    "/objects/<object_id>", view_func=drs_option, methods=["OPTIONS"]
)
drs_blueprint.add_url_rule(
    "/objects/<object_id>", view_func=drs_get_object_info, methods=["GET"]
)
drs_blueprint.add_url_rule(
    "/objects/<object_id>/access/<access_id>",
    view_func=drs_get_access_url,
    methods=["GET"],
)
drs_blueprint.add_url_rule("/service-info", view_func=service_info, methods=["GET"])
