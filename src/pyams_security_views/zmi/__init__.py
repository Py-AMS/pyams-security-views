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

"""PyAMS_security_views.zmi base module

This module provides views and content providers used to display security manager plug-ins.
"""

from pyramid.view import view_config
from zope.interface import Interface, implementer

from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces import ADMIN_USER_NAME, IDirectorySearchPlugin, \
    INTERNAL_USER_NAME, ISecurityManager
from pyams_security.interfaces.base import MANAGE_SECURITY_PERMISSION
from pyams_security_views.zmi.interfaces import ISecurityManagerView, ISecurityMenu
from pyams_site.interfaces import ISiteRoot
from pyams_table.interfaces import IColumn, IValues
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.registry import get_utility
from pyams_utils.url import absolute_url
from pyams_viewlet.manager import viewletmanager_config
from pyams_zmi.helper.container import delete_container_element
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IControlPanelMenu
from pyams_zmi.table import ActionColumn, IconColumn, NameColumn, Table, TableAdminView, \
    TableElementEditor, TrashColumn
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_security_views import _  # pylint: disable=ungrouped-imports


@viewletmanager_config(name='security.menu',
                       context=ISiteRoot, layer=IAdminLayer,
                       manager=IControlPanelMenu, weight=20,
                       permission=MANAGE_SECURITY_PERMISSION,
                       provides=ISecurityMenu)
class SecurityMenu(NavigationMenuItem):
    """Security menu"""

    label = _("Security")
    icon_class = 'fas fa-user-lock'
    href = '#security-plugins.html'


class SecurityPluginsTable(Table):
    """Security plug-ins table"""

    display_if_empty = True

    @property
    def data_attributes(self):
        attributes = super().data_attributes
        sm = get_utility(ISecurityManager)  # pylint: disable=invalid-name
        attributes['table'].update({
            'data-ams-location': absolute_url(sm, self.request),
            'data-ams-order': '1,asc'
        })
        return attributes


@adapter_config(required=(ISiteRoot, IAdminLayer, SecurityPluginsTable),
                provides=IValues)
class SecurityPluginsTableValues(ContextRequestViewAdapter):
    """Security plug-ins values adapter"""

    @property
    def values(self):
        """Security plugins table values getter"""
        sm = get_utility(ISecurityManager)  # pylint: disable=invalid-name
        yield from sm.values()


@adapter_config(name='search',
                required=(ISiteRoot, IAdminLayer, SecurityPluginsTable),
                provides=IColumn)
class SecurityPluginSearchColumn(ActionColumn):
    """Security plug-in search column"""

    hint = _("Search into folder")
    icon_class = 'fas fa-search'
    weight = 1

    href = 'search.html'
    target = '#content'
    modal_target = False

    def render_cell(self, item):
        if IDirectorySearchPlugin.providedBy(item):
            return super().render_cell(item)
        return ''


@adapter_config(name='name',
                required=(ISiteRoot, IAdminLayer, SecurityPluginsTable),
                provides=IColumn)
class SecurityPluginNameColumn(NameColumn):
    """Security plug-in name column"""


@adapter_config(name='enabled',
                required=(ISiteRoot, IAdminLayer, SecurityPluginsTable),
                provides=IColumn)
class SecurityPluginEnabledColumn(IconColumn):
    """Local users search trash column"""

    hint = _("Plug-in is disabled")
    icon_class = 'fa fa-check'

    weight = 90

    @staticmethod
    def checker(item):
        """Enabled column checker"""
        return item.enabled


@adapter_config(name='trash',
                required=(ISiteRoot, IAdminLayer, SecurityPluginsTable),
                provides=IColumn)
class SecurityPluginTrashColumn(TrashColumn):
    """Security plug-in trash column"""

    permission = MANAGE_SECURITY_PERMISSION

    def has_permission(self, item):
        if item.__name__ in (ADMIN_USER_NAME, INTERNAL_USER_NAME):
            return False
        return super().has_permission(item)


@adapter_config(required=(ISecurityManager, IAdminLayer, Interface),
                provides=ITableElementEditor)
class SecurityManagerTableElementEditor(TableElementEditor):
    """Security manager table element editor"""

    view_name = 'admin#security-plugins.html'
    modal_target = False

    def __new__(cls, context, request, view):  # pylint: disable=unused-argument
        if not request.has_permission(MANAGE_SECURITY_PERMISSION, context=context):
            return None
        return TableElementEditor.__new__(cls)

    @property
    def href(self):
        return absolute_url(self.request.root, self.request, self.view_name)


@pagelet_config(name='security-plugins.html', context=ISiteRoot, layer=IPyAMSLayer,
                permission=MANAGE_SECURITY_PERMISSION)
@implementer(ISecurityManagerView)
class SecurityPluginsView(TableAdminView):
    """Security plug-ins view"""

    title = _("Security plug-ins")
    table_class = SecurityPluginsTable
    table_label = _("List of security plug-ins")


@view_config(name='delete-element.json', context=ISecurityManager, request_type=IPyAMSLayer,
             permission=MANAGE_SECURITY_PERMISSION, renderer='json', xhr=True)
def delete_security_plugin(request):
    """Delete security plugin"""
    return delete_container_element(request)
