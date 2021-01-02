#
# Copyright (c) 2015-2020 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_security_views.zmi.manager module

This module provides views and content providers used to manage security manager properties.
"""

from zope.interface import implementer

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IGroup
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces import ISecurityManager
from pyams_security.interfaces.base import MANAGE_SECURITY_PERMISSION
from pyams_security_views.zmi import ISecurityMenu
from pyams_security_views.zmi.interfaces import ISecurityPropertiesEditForm
from pyams_security_views.zmi.widget import SecurityManagerPluginsFieldWidget
from pyams_site.interfaces import ISiteRoot
from pyams_skin.interfaces.viewlet import IHeaderViewletManager
from pyams_skin.viewlet.help import AlertMessage
from pyams_utils.adapter import adapter_config
from pyams_utils.registry import get_utility
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminEditForm, FormGroupChecker
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_security_views import _  # pylint: disable=ungrouped-imports


@viewlet_config(name='security-properties.menu',
                context=ISiteRoot, layer=IAdminLayer,
                manager=ISecurityMenu, weight=10,
                permission=MANAGE_SECURITY_PERMISSION)
class SecurityPropertiesMenu(NavigationMenuItem):
    """Security manager properties menu"""

    label = _("Properties")
    href = '#security-properties.html'


@ajax_form_config(name='security-properties.html', context=ISiteRoot,
                  layer=IPyAMSLayer, permission=MANAGE_SECURITY_PERMISSION)
@implementer(ISecurityPropertiesEditForm)
class SecurityPropertiesEditForm(AdminEditForm):
    """Security manager properties edit form"""

    title = _("Security manager")
    legend = _("Properties")

    fields = Fields(ISecurityManager).select('credentials_plugins_names',
                                             'authentication_plugins_names',
                                             'directory_plugins_names')
    fields['credentials_plugins_names'].widget_factory = SecurityManagerPluginsFieldWidget
    fields['authentication_plugins_names'].widget_factory = SecurityManagerPluginsFieldWidget
    fields['directory_plugins_names'].widget_factory = SecurityManagerPluginsFieldWidget

    def get_content(self):
        return get_utility(ISecurityManager)


@adapter_config(name='security-registration',
                required=(ISiteRoot, IAdminLayer, SecurityPropertiesEditForm),
                provides=IGroup)
class SecurityRegistrationGroup(FormGroupChecker):
    """Security manager registration fields"""

    fields = Fields(ISecurityManager).select('open_registration', 'users_folder')


@viewlet_config(name='security-registration.header',
                context=ISiteRoot, layer=IAdminLayer, view=SecurityRegistrationGroup,
                manager=IHeaderViewletManager, weight=1)
class SecurityRegistrationHeader(AlertMessage):
    """Security registration header"""

    status = 'info'

    _message = _("Open registration can be used when you want external users to be able to "
                 "freely register their user account.\n"
                 "You then have to select the users folder into which their profile will be "
                 "stored.\n"
                 "THIS CAN BE DANGEROUS! You should enable this feature carefully...")
