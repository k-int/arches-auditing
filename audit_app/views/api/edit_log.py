import uuid

from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.generic import View

from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.resource import Resource
from arches.app.models.graph import Graph
from arches.app.models.system_settings import settings
from django.db.models import Subquery, OuterRef, UUIDField
from django.db.models.functions import Cast
from arches.app.utils.response import JSONErrorResponse, JSONResponse

from audit_app.const import EDIT_TYPE_LABELS


class ResourceEditLogAPIView(View):
    def get(self, request):
        # TO DO - ADD SPECIFIC PERMISSION
        if not request.user.is_authenticated:

            return JsonResponse(
                {"message": _("Authentication required.")},
                status=403,
            )
        
        sort_field = request.GET.get('sortField')
        sort_order = request.GET.get('sortOrder')
        
        data_edits = models.EditLog.objects.exclude(
            resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
        )
        filtered_edits = data_edits.filter()

        graph_name_subquery = Graph.objects.filter(
            graphid=Cast(OuterRef('resourceclassid'), UUIDField())
        ).values('name')[:1]

        resource_name_subquery = Resource.objects.filter(
            resourceinstanceid=Cast(OuterRef('resourceinstanceid'), UUIDField())
        ).values('name')[:1]

        card_name_subquery = Card.objects.filter(
            nodegroup_id=Cast(OuterRef('nodegroupid'), UUIDField())
        ).values('name')[:1]

        filtered_edits = filtered_edits.annotate(
            graph_name=Subquery(graph_name_subquery),
            resource_name=Subquery(resource_name_subquery),
            card_name=Subquery(card_name_subquery)
        )

        ALLOWED_SORT_FIELDS = ['resourceinstanceid', 'resource_name', 'graph_name', 'timestamp', 'user_username', 'edittype', 'card_name']

        if sort_field in ALLOWED_SORT_FIELDS:

            if sort_order == 'desc':
                sort_field = f"-{sort_field}"

            filtered_edits = filtered_edits.order_by(sort_field)
        else:
            filtered_edits = filtered_edits.order_by('-timestamp')

        for edit in filtered_edits:
            print(type(edit.card_name))

        permitted_edits = []

        nodegroup_ids = [uuid.UUID(edit.nodegroupid) for edit in filtered_edits if edit.nodegroupid]
        nodegroups_by_id = models.NodeGroup.objects.filter(
            pk__in=nodegroup_ids
        ).in_bulk()

        for edit in filtered_edits:

            if edit.nodegroupid:
                nodegroup = nodegroups_by_id.get(uuid.UUID(edit.nodegroupid))
                if nodegroup and not request.user.has_perm("read_nodegroup", nodegroup):
                    continue

                permitted_edits.append(
                {
                    "editlogid": str(edit.editlogid),
                    "resourceinstanceid": str(edit.resourceinstanceid),
                    "resource_name": edit.resource_name,
                    "graph_name": edit.graph_name,
                    "transactionid": (
                        str(edit.transactionid) if edit.transactionid else None
                    ),
                    "edittype": edit.edittype,
                    "edittype_label": str(EDIT_TYPE_LABELS.get(edit.edittype, edit.edittype)),
                    "timestamp": edit.timestamp.isoformat() if edit.timestamp else None,
                    "userid": edit.userid,
                    "user_firstname": edit.user_firstname,
                    "user_lastname": edit.user_lastname,
                    "user_username": edit.user_username,
                    "user_email": edit.user_email,
                    "nodegroupid": edit.nodegroupid,
                    "tileinstanceid": edit.tileinstanceid,
                    "card_name": edit.card_name,
                    "note": edit.note,
                })
            
        return JSONResponse({"edits": permitted_edits})