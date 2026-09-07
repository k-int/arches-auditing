import json
from pprint import pprint
import uuid
from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test.client import RequestFactory

from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as ResourceGraphImporter,
)

from arches_auditing.views.api.edit_log import ResourceEditLogAPIView

GRAPH_PATH = "tests/fixtures/resource_graphs/test_graph.json"
GRAPH_ID = "500a5aa7-0bbb-4df8-8c78-e361c8faab35"
NODEGROUP_ID = "58ea0324-6592-11f1-a941-95721ea55e2b"
NODE_ID = "1e526804-6593-11f1-a941-95721ea55e2b"
RESOURCE_ID = "e6ca165e-a7bc-4867-803a-c71f83dc9bd6"

class EditLogGetViewTests(TestCase):
    """HTTP-level tests for GET /edit-log."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        with open(GRAPH_PATH, "r") as f:
            archesfile = JSONDeserializer().deserialize(f)
            ResourceGraphImporter(archesfile["graph"], overwrite_graphs=True)

        cls.user = User.objects.get(username="admin")

        #### create edit log

    def _create_basic_edit_log(self):
        """Helper to set up a standard tile lifecycle, including resource creation (Create -> Tile Create -> Tile Edit -> Tile Delete)"""
        resource = Resource.objects.create(
            graph_id=GRAPH_ID,
            name="New Resource",
            resourceinstanceid=RESOURCE_ID,
        )

        new_tile = Tile.get_blank_tile_from_nodegroup_id(
                nodegroup_id=NODEGROUP_ID,
                resourceid=RESOURCE_ID,
            )

        new_tile.data = {NODE_ID: "First string"}

        new_tile.save(
            resource_creation=True,
            user=self.user
        )

        new_tile.data = {NODE_ID: "Second string"}

        new_tile.save(
            user=self.user
        )

        tile_id = str(new_tile.tileid)

        new_tile.delete()

        resource.delete()

        return tile_id

    def _assert_valid_uuid(self, val, field_name):
        """Helper method to validate UUID format for any field"""
        try:
            uuid.UUID(val)
        except ValueError:
            self.fail(f"'{field_name}' value '{val}' is not a valid UUID string")

    def _assert_valid_timestamp(self, val, field_name):
        try:
            datetime.fromisoformat(val)
        except ValueError:
            self.fail(f"{field_name} value '{val}' is not a valid ISO datetime string")

    def test_edit_contents(self):

        tile_id = self._create_basic_edit_log()

        self.client.force_login(self.user)
        response = self.client.get(reverse("audit-app-edit-log"))
        response_data = response.json()

        #### Test counts data

        self.assertEqual(response_data["total_count"], 5)
        self.assertEqual(response_data["action_counts"], {"create": 1, 'tile create': 1, 'tile edit': 1, 'tile delete': 1, "delete": 1})
        self.assertEqual(len(response_data["edits"]), 5)

        #### Combined validation for common fields

        for edit in response_data["edits"]:
            self._assert_valid_uuid(edit['editlogid'], 'editlogid')
            self._assert_valid_uuid(edit['transactionid'], 'transactionid')
            self._assert_valid_timestamp(edit['timestamp'], 'timestamp')

            self.assertEqual(edit["graph_name"], "Test resource model")
            self.assertEqual(edit["resourceinstanceid"], RESOURCE_ID)

            self.assertIsNone(edit["resource_name"]) # resource name is found via the resourceinstanceid, so not available for deleted resources

            if edit["edittype"] not in ["create", "delete"]:
                self.assertEqual(edit["tileinstanceid"], tile_id)
                self.assertEqual(edit["nodegroupid"], NODEGROUP_ID)

        #### Resource creation

        resource_creation_edit = response_data["edits"][4]

        self.assertEqual(resource_creation_edit["edittype"], "create")
        self.assertEqual(resource_creation_edit["edittype_label"], 'Resource Created')

        self.assertIsNone(resource_creation_edit["new_value"])
        self.assertIsNone(resource_creation_edit["old_value"])
        self.assertIsNone(resource_creation_edit["nodegroupid"])
        self.assertIsNone(resource_creation_edit["tileinstanceid"])
        self.assertIsNone(resource_creation_edit["user_username"])

        #### Tile creation

        tile_create_edit = response_data["edits"][3]

        self.assertEqual(tile_create_edit["edittype"], "tile create")
        self.assertEqual(tile_create_edit["edittype_label"], 'Tile Created')
        self.assertEqual(tile_create_edit["new_value"], {NODE_ID: "First string"})
        self.assertEqual(tile_create_edit["old_value"], {})
        self.assertEqual(tile_create_edit["note"], "resource creation")
        self.assertEqual(tile_create_edit["user_username"], self.user.username)

        #### Tile edit

        tile_update_edit = response_data["edits"][2]
    
        self.assertEqual(tile_update_edit["edittype"], "tile edit")
        self.assertEqual(tile_update_edit["edittype_label"], 'Tile Updated')
        self.assertEqual(tile_update_edit["new_value"], {NODE_ID: "Second string"})
        self.assertEqual(tile_update_edit["old_value"], {NODE_ID: "First string"})
        self.assertEqual(tile_update_edit["note"], "")
        self.assertEqual(tile_update_edit["user_username"], self.user.username)

        #### Tile delete

        tile_delete_edit = response_data["edits"][1]
    
        self.assertEqual(tile_delete_edit["edittype"], "tile delete")
        self.assertEqual(tile_delete_edit["edittype_label"], 'Tile Deleted')
        self.assertEqual(tile_delete_edit["old_value"], {NODE_ID: "Second string"})
        self.assertEqual(tile_delete_edit["note"], "")
        self.assertEqual(tile_delete_edit["user_username"], '') # user cannot be passed directly to tile.delete, only via a request

        self.assertIsNone(tile_delete_edit["new_value"])

        #### Resource deletion

        delete_edit = response_data["edits"][0]

        self.assertEqual(delete_edit["edittype"], "delete")
        self.assertEqual(delete_edit["edittype_label"], 'Resource Deleted')

        self.assertIsNone(delete_edit["note"]) # none because no display name is set for the test graph
        self.assertIsNone(delete_edit["new_value"])
        self.assertIsNone(delete_edit["old_value"])
        self.assertIsNone(delete_edit["nodegroupid"])
        self.assertIsNone(delete_edit["tileinstanceid"])
        self.assertIsNone(delete_edit["user_username"])