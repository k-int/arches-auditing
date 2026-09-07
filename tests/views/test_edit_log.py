import json
from pprint import pprint
import uuid
from datetime import datetime

from unittest.mock import ANY
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test.client import RequestFactory

from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as ResourceGraphImporter,
)

from arches_auditing.views.api.edit_log import ResourceEditLogAPIView


class EditLogGetViewTests(TestCase):
    """HTTP-level tests for GET /edit-log."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        graph_path = "tests/fixtures/resource_graphs/test_graph.json"

        cls.resourceid = "e6ca165e-a7bc-4867-803a-c71f83dc9bd6"

        with open(graph_path, "r") as f:
            archesfile = JSONDeserializer().deserialize(f)
            ResourceGraphImporter(archesfile["graph"], overwrite_graphs=True)

        cls.user = User.objects.get(username="admin")

        #### create edit log

        resource = Resource.objects.create(
            graph_id="500a5aa7-0bbb-4df8-8c78-e361c8faab35",
            name="New Resource",
            resourceinstanceid=cls.resourceid,
        )

        new_tile = Tile.get_blank_tile_from_nodegroup_id(
                nodegroup_id="58ea0324-6592-11f1-a941-95721ea55e2b",
                resourceid=cls.resourceid,
            )

        new_tile.data = {"1e526804-6593-11f1-a941-95721ea55e2b": "First string"}

        new_tile.save(
            resource_creation=True,
            user=cls.user
        )

        cls.tile_id = str(new_tile.tileid)

        new_tile.data = {"1e526804-6593-11f1-a941-95721ea55e2b": "Second string"}

        new_tile.save(
            user=cls.user
        )

        new_tile.delete()

    def _assert_valid_uuid(self, val, field_name):
        """Helper method to validate UUID format for any field."""
        try:
            uuid.UUID(val)
        except ValueError:
            self.fail(f"'{field_name}' value '{val}' is not a valid UUID string")

    def _assert_valid_timestamp(self, val, field_name):
        try:
            datetime.fromisoformat(val)
        except ValueError:
            self.fail(f"{field_name} value '{val}' is not a valid ISO datetime string")

    def test_tile_lifecycle(self):

        factory = RequestFactory()
        request = factory.get(reverse("audit-app-edit-log"))
        request.user = self.user

        view_function = ResourceEditLogAPIView.as_view()
        response = view_function(request)
        response_data = json.loads(response.content.decode("utf-8"))
        # pprint(response_data)

        #### Resource creation

        resource_creation_edit = response_data["edits"][3]
        
        self._assert_valid_uuid(resource_creation_edit['editlogid'], 'editlogid')
        self._assert_valid_uuid(resource_creation_edit['transactionid'], 'transactionid')
        self._assert_valid_timestamp(resource_creation_edit['timestamp'], 'timestamp')

        self.assertEqual(resource_creation_edit["edittype"], "create")
        self.assertEqual(resource_creation_edit["edittype_label"], 'Resource Created')
        self.assertEqual(resource_creation_edit["resource_name"], "New Resource")
        self.assertEqual(resource_creation_edit["graph_name"], "Test resource model")
        self.assertEqual(resource_creation_edit["resourceinstanceid"], self.resourceid)

        self.assertIsNone(resource_creation_edit["new_value"])
        self.assertIsNone(resource_creation_edit["old_value"])
        self.assertIsNone(resource_creation_edit["nodegroupid"])
        self.assertIsNone(resource_creation_edit["tileinstanceid"])
        self.assertIsNone(resource_creation_edit["user_username"])

        self.assertEqual(response_data["total_count"], 4)
        self.assertEqual(response_data["action_counts"], {"create": 1, 'tile create': 1, 'tile edit': 1, 'tile delete': 1})
        self.assertEqual(len(response_data["edits"]), 4)

        #### Tile creation

        tile_create_edit = response_data["edits"][2]
        pprint(tile_create_edit)

        self._assert_valid_uuid(tile_create_edit['editlogid'], 'editlogid')
        self._assert_valid_uuid(tile_create_edit['transactionid'], 'transactionid')
        self._assert_valid_timestamp(tile_create_edit['timestamp'], 'timestamp')

        self.assertEqual(tile_create_edit["edittype"], "tile create")
        self.assertEqual(tile_create_edit["edittype_label"], 'Tile Created')
        self.assertEqual(tile_create_edit["graph_name"], "Test resource model")
        self.assertEqual(tile_create_edit["resourceinstanceid"], self.resourceid)
        self.assertEqual(tile_create_edit["resource_name"], 'New Resource')
        self.assertEqual(tile_create_edit["new_value"], {"1e526804-6593-11f1-a941-95721ea55e2b": "First string"})
        self.assertEqual(tile_create_edit["old_value"], {})
        self.assertEqual(tile_create_edit["note"], "resource creation")
        self.assertEqual(tile_create_edit["nodegroupid"], "58ea0324-6592-11f1-a941-95721ea55e2b")
        self.assertEqual(tile_create_edit["tileinstanceid"], self.tile_id)
        self.assertEqual(tile_create_edit["user_username"], self.user.username)

        #### Tile edit

        tile_update_edit = response_data["edits"][1]

        self._assert_valid_uuid(tile_update_edit['editlogid'], 'editlogid')
        self._assert_valid_uuid(tile_update_edit['transactionid'], 'transactionid')
        self._assert_valid_timestamp(tile_update_edit['timestamp'], 'timestamp')
    
        self.assertEqual(tile_update_edit["edittype"], "tile edit")
        self.assertEqual(tile_update_edit["edittype_label"], 'Tile Updated')
        self.assertEqual(tile_update_edit["graph_name"], "Test resource model")
        self.assertEqual(tile_update_edit["resourceinstanceid"], self.resourceid)
        self.assertEqual(tile_update_edit["resource_name"], 'New Resource')
        self.assertEqual(tile_update_edit["new_value"], {"1e526804-6593-11f1-a941-95721ea55e2b": "Second string"})
        self.assertEqual(tile_update_edit["old_value"], {"1e526804-6593-11f1-a941-95721ea55e2b": "First string"})
        self.assertEqual(tile_update_edit["note"], "")
        self.assertEqual(tile_update_edit["nodegroupid"], "58ea0324-6592-11f1-a941-95721ea55e2b")
        self.assertEqual(tile_update_edit["tileinstanceid"], self.tile_id)
        self.assertEqual(tile_update_edit["user_username"], self.user.username)

        #### Tile delete

        tile_delete_edit = response_data["edits"][0]

        self._assert_valid_uuid(tile_delete_edit['editlogid'], 'editlogid')
        self._assert_valid_uuid(tile_delete_edit['transactionid'], 'transactionid')
        self._assert_valid_timestamp(tile_delete_edit['timestamp'], 'timestamp')
    
        self.assertEqual(tile_delete_edit["edittype"], "tile delete")
        self.assertEqual(tile_delete_edit["edittype_label"], 'Tile Deleted')
        self.assertEqual(tile_delete_edit["graph_name"], "Test resource model")
        self.assertEqual(tile_delete_edit["resourceinstanceid"], self.resourceid)
        self.assertEqual(tile_delete_edit["resource_name"], 'New Resource')
        self.assertEqual(tile_delete_edit["old_value"], {"1e526804-6593-11f1-a941-95721ea55e2b": "Second string"})
        self.assertEqual(tile_delete_edit["note"], "")
        self.assertEqual(tile_delete_edit["nodegroupid"], "58ea0324-6592-11f1-a941-95721ea55e2b")
        self.assertEqual(tile_delete_edit["tileinstanceid"], self.tile_id)
        self.assertEqual(tile_delete_edit["user_username"], '') # user cannot be passed directly to tile.delete, only via a request

        self.assertIsNone(tile_delete_edit["new_value"])

    def test_resource_deletion(self):

        resource = Resource.objects.get(pk="e6ca165e-a7bc-4867-803a-c71f83dc9bd6")
        resource.delete()

        factory = RequestFactory()
        request = factory.get(reverse("audit-app-edit-log"))
        request.user = self.user

        view_function = ResourceEditLogAPIView.as_view()
        response = view_function(request)
        response_data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response_data["total_count"], 5)
        self.assertEqual(response_data["action_counts"], {"create": 1, 'tile create': 1, 'tile edit': 1, 'tile delete': 1, "delete": 1})
        self.assertEqual(len(response_data["edits"]), 5)

        edit = response_data["edits"][0]

        self._assert_valid_uuid(edit['editlogid'], 'editlogid')
        self._assert_valid_uuid(edit['transactionid'], 'transactionid')
        self._assert_valid_timestamp(edit['timestamp'], 'timestamp')

        self.assertEqual(edit["edittype"], "delete")
        self.assertEqual(edit["edittype_label"], 'Resource Deleted')
        self.assertEqual(edit["graph_name"], "Test resource model")
        self.assertEqual(edit["resourceinstanceid"], self.resourceid)

        self.assertIsNone(edit["resource_name"], None) # resource name is found via the resourceinstanceid, so not available for deleted resources
        self.assertIsNone(edit["note"]) # none because no display name is set for the test graph
        self.assertIsNone(edit["new_value"])
        self.assertIsNone(edit["old_value"])
        self.assertIsNone(edit["nodegroupid"])
        self.assertIsNone(edit["tileinstanceid"])
        self.assertIsNone(edit["user_username"])