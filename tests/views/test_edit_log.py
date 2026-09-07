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

        with open(graph_path, "r") as f:
            archesfile = JSONDeserializer().deserialize(f)
            ResourceGraphImporter(archesfile["graph"], overwrite_graphs=True)

        cls.user = User.objects.get(username="admin")
        # self.client.force_login(user)


    def test_resource_creation(self):

        resource = Resource.objects.create(
            graph_id="500a5aa7-0bbb-4df8-8c78-e361c8faab35",
            name="New Resource",
            resourceinstanceid="e6ca165e-a7bc-4867-803a-c71f83dc9bd6",
        )

        factory = RequestFactory()
        request = factory.get(reverse("audit-app-edit-log"))
        request.user = self.user

        view_function = ResourceEditLogAPIView.as_view()
        response = view_function(request)
        response_data = json.loads(response.content.decode("utf-8"))

        # response = self.client.get(reverse("audit-app-edit-log"))

        self.assertEqual(response_data["total_count"], 1)
        self.assertEqual(response_data["action_counts"], {"create": 1})
        self.assertEqual(len(response_data["edits"]), 1)

        edit = response_data["edits"][0]

        try:
            uuid.UUID(edit['editlogid'])
        except ValueError:
            self.fail("editlogid is not a valid UUID string")

        try:
            uuid.UUID(edit['transactionid'])
        except ValueError:
            self.fail("transactionid is not a valid UUID string")

        try:
            datetime.fromisoformat(edit['timestamp'])
        except ValueError:
            self.fail("timestamp is not a valid ISO datetime string")

        self.assertEqual(edit["edittype"], "create")
        self.assertEqual(edit["edittype_label"], 'Resource Created')
        self.assertEqual(edit["resource_name"], "New Resource")
        self.assertEqual(edit["graph_name"], "Test resource model")
        self.assertEqual(edit["resourceinstanceid"], str(resource.resourceinstanceid))

        self.assertIsNone(edit["new_value"])
        self.assertIsNone(edit["old_value"])
        self.assertIsNone(edit["nodegroupid"])
        self.assertIsNone(edit["tileinstanceid"])
        self.assertIsNone(edit["user_username"])

    def test_resource_deletion(self):

        resource = Resource.objects.create(
            graph_id="500a5aa7-0bbb-4df8-8c78-e361c8faab35",
            name="New Resource",
            resourceinstanceid="e6ca165e-a7bc-4867-803a-c71f83dc9bd6",
        )

        resourceinstanceid = str(resource.resourceinstanceid)

        resource.delete()

        factory = RequestFactory()
        request = factory.get(reverse("audit-app-edit-log"))
        request.user = self.user

        view_function = ResourceEditLogAPIView.as_view()
        response = view_function(request)
        response_data = json.loads(response.content.decode("utf-8"))
        # pprint(response_data)

        self.assertEqual(response_data["total_count"], 2)
        self.assertEqual(response_data["action_counts"], {"create": 1, 'delete': 1})
        self.assertEqual(len(response_data["edits"]), 2)

        edit = response_data["edits"][0]

        try:
            uuid.UUID(edit['editlogid'])
        except ValueError:
            self.fail("editlogid is not a valid UUID string")

        try:
            uuid.UUID(edit['transactionid'])
        except ValueError:
            self.fail("transactionid is not a valid UUID string")

        try:
            datetime.fromisoformat(edit['timestamp'])
        except ValueError:
            self.fail("timestamp is not a valid ISO datetime string")

        self.assertEqual(edit["edittype"], "delete")
        self.assertEqual(edit["edittype_label"], 'Resource Deleted')
        self.assertEqual(edit["graph_name"], "Test resource model")
        self.assertEqual(edit["resourceinstanceid"], resourceinstanceid)

        self.assertIsNone(edit["resource_name"], None) # note that resource name is found via the resourceinstanceid, so not available for deleted resources
        self.assertIsNone(edit["note"]) # none because no display name is set for the test graph
        self.assertIsNone(edit["new_value"])
        self.assertIsNone(edit["old_value"])
        self.assertIsNone(edit["nodegroupid"])
        self.assertIsNone(edit["tileinstanceid"])
        self.assertIsNone(edit["user_username"])


