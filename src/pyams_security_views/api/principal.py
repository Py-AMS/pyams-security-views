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

from colander import MappingSchema, SchemaNode, SequenceSchema, String
from cornice import Service
from cornice.validators import colander_querystring_validator
from pyramid.httpexceptions import HTTPOk

from pyams_security.interfaces import ISecurityManager
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_security_views.interfaces import REST_PRINCIPALS_SEARCH_ROUTE
from pyams_utils.registry import query_utility


__docformat__ = 'restructuredtext'

from pyams_security_views import _


class PrincipalsSearchQuerySchema(MappingSchema):
    """Principals search schema"""
    term = SchemaNode(String(),
                      description=_("Principals search string"))


class PrincipalResultSchema(MappingSchema):
    """Principal result schema"""
    id = SchemaNode(String(),
                    description=_("Principal ID"))
    text = SchemaNode(String(),
                      description=_("Principal title"))


class PrincipalsSearchResults(SequenceSchema):
    """"""
    result = PrincipalResultSchema()


class PrincipalsSearchResultsSchema(MappingSchema):
    """Principals search results schema"""
    results = PrincipalsSearchResults(description=_("Results list"))


search_responses = {
    HTTPOk.code: PrincipalsSearchResultsSchema(description=_("Search results")),
}


service = Service(name=REST_PRINCIPALS_SEARCH_ROUTE,
                  pyramid_route=REST_PRINCIPALS_SEARCH_ROUTE,
                  description="Principals management")


@service.get(permission=VIEW_SYSTEM_PERMISSION,
             schema=PrincipalsSearchQuerySchema(),
             validators=(colander_querystring_validator,),
             response_schemas=search_responses)
def get_principals(request):
    """Returns list of principals matching given query"""
    query = request.validated.get('term')
    if not query:
        return []
    manager = query_utility(ISecurityManager)
    return {
        'results': [{
            'id': principal.id,
            'text': principal.title
        } for principal in manager.find_principals(query)]
    }
