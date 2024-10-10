import json
import logging
import six

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.api_token as api_token
from ckan import model
from ckan.common import g, request

from ckanext.drs import views
from ckanext.drs import actions
from ckanext.drs import auth

log = logging.getLogger(__name__)


class DrsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IBlueprint, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IAuthenticator, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "drs")

    # ITemplateHelpers
    def get_helpers(self):
        return {}

    # IResourceController
    def before_show(self, resource_dict):
        # check for drs resource
        # drs_res = utils.get_drs_resource(resource_dict)
        pass

    # IBlueprint
    def get_blueprint(self):
        # return a blueprint object that can be used to register routes
        return views.drs_blueprint

    # IActions
    def get_actions(self):
        return {
            "drs_option_show": actions.option_show,
            "drs_get_object_info": actions.get_object_info,
            "drs_service_info_show": actions.service_info_show,
            "drs_get_access_url": actions.drs_get_access_url,
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            "drs_option_show": auth.option_show,
            "drs_get_object_info": auth.get_object_info,
            "drs_get_access_url": auth.drs_get_access_url,
        }

    # IAuthenticator
    def identify(self):
        def set_user_for_current_request(user):
            from flask import current_app

            current_app.login_manager._update_request_context_with_user(user)

        authorization = None
        if not authorization:
            authorization = request.environ.get("HTTP_AUTHORIZATION", None)
        if not authorization:
            authorization = request.environ.get("Authorization", None)
        if not authorization:
            # no header
            return

        # Need to look for Bearer header
        if not authorization.startswith("Bearer "):
            # not a bearer token
            return

        # Split and see if token
        bearer_token = authorization.split(" ", 1)[-1]
        bearer_token = six.ensure_text(bearer_token, errors="ignore")
        log.debug(f"Received Bearer Token: {bearer_token[:10]}[...]")

        if not bearer_token:
            return

        user = None
        # if 2.9 or earlier, API key
        if not toolkit.check_ckan_version(min_version="2.10"):
            query = model.Session.query(model.User)
            user = query.filter_by(apikey=bearer_token).first()

        if not user:
            user = api_token.get_user_from_token(bearer_token)

        if not user:
            return

        g.user = user.name
        g.userobj = user

        # IAuthenticator interface is presently broken in CKAN 2.10
        #
        # It is discussed in ckan/ckan#7581
        # Adopting interim fix described in ckan/ckan#7591
        #
        if toolkit.check_ckan_version(min_version="2.10"):
            set_user_for_current_request(user)

        return
