from flask import Blueprint, Response, make_response, request as flask_request
import json

from ckan.plugins import toolkit as tk
from ckan.common import config

import ckan.views.api as api
import logging


log = logging.getLogger(__name__)


def _oidc_context():
    """Return an ignore_auth context if the request carries a valid OIDC Bearer token.

    Galaxy calls CKAN's DRS endpoints with the user's Auth0 Bearer token
    (via the BPA DRS file source configured with oidc_auth_provider: auth0).
    We verify the JWT signature against the OIDC provider's JWKS and, if valid,
    trust the authentication — the user proved their identity via Auth0.
    """
    auth = flask_request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    try:
        import jwt
        from jwt import PyJWKClient
        base_url = config.get("ckanext.oidc_pkce.base_url", "").rstrip("/")
        if not base_url:
            return None
        client = PyJWKClient(f"{base_url}/.well-known/jwks.json")
        key = client.get_signing_key_from_jwt(token)
        jwt.decode(token, key.key, algorithms=["RS256"])
        log.info("drs: valid OIDC Bearer token — using ignore_auth context")
        return {"ignore_auth": True}
    except Exception as e:
        log.debug("drs: OIDC Bearer validation failed: %s", e)
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
        context = _oidc_context() or {"user": tk.g.user, "auth_user_obj": tk.g.userobj}
        return tk.get_action("drs_get_object_info")(context, {"object_id": object_id})
    except tk.ObjectNotFound:
        return _drs_error(404, f"Not Found: object '{object_id}' does not exist")
    except tk.NotAuthorized:
        return _drs_error(403, f"Forbidden: you do not have permission to access object '{object_id}'")


def drs_get_access_url(object_id, access_id):
    try:
        context = _oidc_context() or {"user": tk.g.user, "auth_user_obj": tk.g.userobj}
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
