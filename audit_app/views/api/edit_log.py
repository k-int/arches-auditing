import uuid

from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.generic import View

from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
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
        
        # get all edits
        filtered_edits = (models.EditLog.objects.exclude(
            resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
        ))

        # get all edited resources
        edited_resources_ids = list({edit.resourceinstanceid for edit in filtered_edits})
        
        edited_resources = Resource.objects.filter(
            resourceinstanceid__in=edited_resources_ids
        ).distinct().select_related("graph")

        resource_lookup = {str(resource.pk): resource for resource in edited_resources}

        graph_ids = {resource.graph_id for resource in edited_resources}
        all_cards = Card.objects.filter(graph_id__in=graph_ids)

        graph_card_map = {}
        for card in all_cards:
            graph_card_map[str(card.nodegroup_id)] = card.name

        permitted_edits = []

        for edit in filtered_edits:

            resource_instance = resource_lookup.get(edit.resourceinstanceid)
            graph_name = resource_instance.graph.name
            resource_name = resource_instance.name

            nodegroup_id = edit.nodegroupid

            card_name = graph_card_map.get(str(nodegroup_id), _("Unknown Card"))

            nodegroups_by_id = models.NodeGroup.objects.filter(
                pk__in=[uuid.UUID(edit.nodegroupid) for edit in filtered_edits if edit.nodegroupid]
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
                        "resource_name": str(resource_name),
                        "graph_name": graph_name,
                        "transactionid": (
                            str(edit.transactionid) if edit.transactionid else None
                        ),
                        "edittype": edit.edittype,
                        "edittype_label": EDIT_TYPE_LABELS.get(edit.edittype, edit.edittype),
                        "timestamp": edit.timestamp.isoformat() if edit.timestamp else None,
                        "userid": edit.userid,
                        "user_firstname": edit.user_firstname,
                        "user_lastname": edit.user_lastname,
                        "user_username": edit.user_username,
                        "user_email": edit.user_email,
                        "nodegroupid": edit.nodegroupid,
                        "tileinstanceid": edit.tileinstanceid,
                        "card_name": card_name,
                        "note": edit.note,
                    })
            
        return JSONResponse({"edits": permitted_edits})