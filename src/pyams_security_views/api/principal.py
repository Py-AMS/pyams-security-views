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

"""PyAMS_security_views.api.principal module

This module only provides a small Cornice API to search for principals.
"""

from cornice import Service

from pyams_security.interfaces import ISecurityManager
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_utils.registry import query_utility


__docformat__ = 'restructuredtext'


service = Service(name='principals',
                  path='/api/security/principals',
                  description="Principals management")


@service.get(permission=VIEW_SYSTEM_PERMISSION)
def get_principals(request):
    """Returns list of principals matching given query"""
    query = request.params.get('term')
    if not query:
        return []
    manager = query_utility(ISecurityManager)
    return {
        'results': [{
            'id': principal.id,
            'text': principal.title
        } for principal in manager.find_principals(query)]
    }
