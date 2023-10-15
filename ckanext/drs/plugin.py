import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.drs import views
from ckanext.drs import utils
from ckanext.drs import actions
from ckanext.drs import auth


class DrsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IBlueprint, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets','drs')


    # ITemplateHelpers
    def get_helpers(self):
        return {}

    # IResourceController
    def before_show(self, resource_dict):
        # check for drs resource
        #drs_res = utils.get_drs_resource(resource_dict)
        pass 


    # IBlueprint
    def get_blueprint(self):
        # return a blueprint object that can be used to register routes
        return views.drs_blueprint
    
    # IActions
    def get_actions(self):
        return {
            'drs_option_show': actions.option_show,
            'drs_get_object_info': actions.get_object_info,
            'drs_service_info_show': actions.service_info_show
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'drs_option_show': auth.option_show,
            'drs_get_object_info': auth.get_object_info,
        }