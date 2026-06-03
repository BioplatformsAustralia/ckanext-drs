from flask import Blueprint, Response, make_response
import json

from ckan.plugins import toolkit as tk
from ckan.common import request

import ckan.views.api as api
import logging

log = logging.getLogger(__name__)


def _context_from_bearer_token():
    """Return a CKAN user context from an Auth0 Bearer token, or None.

    Delegates to ckanext-oidc-pkce-bpa which owns Auth0 token validation.
    CKAN's normal per-resource permission checks still apply.
    """
    try:
        from ckanext.oidc_pkce_bpa.utils import ckan_context_from_bearer_token
        return ckan_context_from_bearer_token(request.headers.get("Authorization", ""))
    except ImportError:
        return None


drs_blueprint = Blueprint("drs", __name__, url_prefix="/ga4gh/drs/v1")


def _drs_error(status_code, msg):
    body = json.dumps({"status_code": status_code, "msg": msg}) + "\n"
    return make_response(body, status_code, {"Content-Type": "application/json"})


def drs_option(object_id):
    log.info("***************** OBJECT ID" + object_id)
    try:
        return tk.get_action("drs_option_show")({}, {"object_id": object_id})
    except tk.ObjectNotFound:
        return _drs_error(404, f"Not Found: object '{object_id}' does not exist")
    except tk.NotAuthorized:
        return _drs_error(403, f"Forbidden: you do not have permission to access object '{object_id}'")


def drs_get_object_info(object_id):
    try:
        # Session auth takes precedence; Bearer token is only for server-to-server
        # callers (e.g. Galaxy) that have no CKAN session.
        context = {"user": tk.g.user, "auth_user_obj": tk.g.userobj}
        if not tk.g.user:
            context = _context_from_bearer_token() or context
        return tk.get_action("drs_get_object_info")(context, {"object_id": object_id})
    except tk.ObjectNotFound:
        return _drs_error(404, f"Not Found: object '{object_id}' does not exist")
    except tk.NotAuthorized:
        return _drs_error(403, f"Forbidden: you do not have permission to access object '{object_id}'")


def drs_get_access_url(object_id, access_id):
    try:
        # Session auth takes precedence; Bearer token is only for server-to-server
        # callers (e.g. Galaxy) that have no CKAN session.
        context = {"user": tk.g.user, "auth_user_obj": tk.g.userobj}
        if not tk.g.user:
            context = _context_from_bearer_token() or context
        response = tk.get_action("drs_get_access_url")(
            context, {"access_id": access_id, "object_id": object_id}
        )
        # CKAN may return a redirect Response object (instead of raising) when
        # auth fails in a web-request context — convert that to a proper 403.
        if isinstance(response, Response) and response.status_code in (301, 302, 303, 307, 308):
            return _drs_error(403, f"Forbidden: you do not have permission to access object '{object_id}'")
        return response
    except tk.NotAuthorized:
        return _drs_error(403, f"Forbidden: you do not have permission to access object '{object_id}'")
    except tk.ObjectNotFound:
        return _drs_error(404, f"Not Found: object '{object_id}' does not exist")
    except tk.ValidationError as e:
        msg = next(iter(e.error_dict.values()), "Bad Request") if e.error_dict else "Bad Request"
        if isinstance(msg, list):
            msg = msg[0]
        return _drs_error(400, str(msg))


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
