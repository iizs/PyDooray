import unittest
from unittest.mock import patch, MagicMock, ANY
import dooray
from dooray.DoorayExceptions import BadHttpResponseStatusCode
from tests.fixtures.responses import (
    RESPONSE_HEADER_SUCCESS,
    PROJECT_RESPONSE,
    RELATION_RESPONSE,
    WORKFLOW_LIST_RESPONSE,
    MILESTONE_RESPONSE,
    TAG_RESPONSE,
    POST_RESPONSE,
    POST_LIST_RESPONSE,
    POST_LOG_RESPONSE,
)


# Reusable milestone list response
MILESTONE_LIST_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": [MILESTONE_RESPONSE["result"]],
    "totalCount": 1
}

# Reusable post log list response
POST_LOG_LIST_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": [POST_LOG_RESPONSE["result"]],
    "totalCount": 1
}

# Reusable member response
PROJECT_MEMBER_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": {
        "organizationMemberId": "member-1",
        "role": "member"
    }
}

# Reusable member group response
MEMBER_GROUP_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": {
        "id": "mg-1",
        "code": "group-1",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "project": {
            "id": "proj-1",
            "code": "test-project"
        }
    }
}

# Reusable email address response
EMAIL_ADDRESS_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": {
        "id": "email-1",
        "name": "Test Email",
        "emailAddress": "test@dooray.com"
    }
}

# Template list response
TEMPLATE_LIST_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": [
        {
            "id": "tmpl-1",
            "project": {"id": "proj-1", "code": "test-project"},
            "templateName": "Bug Report",
            "subject": "Bug:",
            "body": {"mimeType": "text/x-markdown", "content": "template body"},
            "users": {"to": [], "cc": []},
            "priority": "normal",
            "isDefault": False,
            "tags": []
        }
    ],
    "totalCount": 1
}

# Single template response
TEMPLATE_RESPONSE: dict = {
    **RESPONSE_HEADER_SUCCESS,
    "result": TEMPLATE_LIST_RESPONSE["result"][0]
}


class TestDoorayProject(unittest.TestCase):
    def setUp(self):
        self._dooray = dooray.Dooray(token="test-token")

    def _make_mock_resp(self, json_data):
        """Helper to create a mock response with status 200."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = ""
        mock_resp.json.return_value = json_data
        return mock_resp

    # --- Project > Projects ---

    @patch("requests.request")
    def test_is_creatable_true(self, mock_request):
        """Returns True when API returns 200."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        result = self._dooray.project.is_creatable("new-project")

        self.assertTrue(result)

    @patch("requests.request")
    def test_is_creatable_false(self, mock_request):
        """Returns False when BadHttpResponseStatusCode raised."""
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_request.side_effect = BadHttpResponseStatusCode(mock_resp)

        result = self._dooray.project.is_creatable("existing-project")

        self.assertFalse(result)

    @patch("requests.request")
    def test_create_project(self, mock_request):
        """Verify correct body: code, description, scope."""
        mock_request.return_value = self._make_mock_resp(RELATION_RESPONSE)

        result = self._dooray.project.create("my-proj", "desc", "public")

        call_kwargs = mock_request.call_args
        body = call_kwargs.kwargs["json"]
        self.assertEqual(body["code"], "my-proj")
        self.assertEqual(body["description"], "desc")
        self.assertEqual(body["scope"], "public")
        self.assertEqual(result.result.id, "5555555555")

    @patch("requests.request")
    def test_get_project(self, mock_request):
        """Verify endpoint and Project parsing."""
        mock_request.return_value = self._make_mock_resp(PROJECT_RESPONSE)

        result = self._dooray.project.get("proj-1")

        call_args = mock_request.call_args
        self.assertIn("/project/v1/projects/proj-1", call_args[0][1])
        self.assertEqual(result.result.code, "test-project")

    @patch("requests.request")
    def test_get_workflows(self, mock_request):
        """Verify list response of Workflow."""
        mock_request.return_value = self._make_mock_resp(WORKFLOW_LIST_RESPONSE)

        result = self._dooray.project.get_workflows("proj-1")

        self.assertEqual(len(result.result), 3)
        self.assertEqual(result.result[0].name, "Registered")
        self.assertEqual(result.result[1].workflow_class, "working")

    # --- Project > EmailAddress ---

    @patch("requests.request")
    def test_create_email_address(self, mock_request):
        """Verify body: emailAddress, name."""
        mock_request.return_value = self._make_mock_resp(RELATION_RESPONSE)

        self._dooray.project.create_email_address("proj-1", "test@dooray.com", "Test")

        body = mock_request.call_args.kwargs["json"]
        self.assertEqual(body["emailAddress"], "test@dooray.com")
        self.assertEqual(body["name"], "Test")

    @patch("requests.request")
    def test_get_email_address(self, mock_request):
        """Verify endpoint with email_address_id."""
        mock_request.return_value = self._make_mock_resp(EMAIL_ADDRESS_RESPONSE)

        result = self._dooray.project.get_email_address("proj-1", "email-1")

        call_args = mock_request.call_args
        self.assertIn("/email-addresses/email-1", call_args[0][1])
        self.assertEqual(result.result.email_address, "test@dooray.com")

    # --- Project > Tags ---

    @patch("requests.request")
    def test_create_tag(self, mock_request):
        """Verify body: name, color."""
        mock_request.return_value = self._make_mock_resp(RELATION_RESPONSE)

        self._dooray.project.create_tag("proj-1", "bug", "ff0000")

        body = mock_request.call_args.kwargs["json"]
        self.assertEqual(body["name"], "bug")
        self.assertEqual(body["color"], "ff0000")

    def test_create_tag_assertion_on_none(self):
        """Verify assertion errors when name or color is None."""
        with self.assertRaises(AssertionError):
            self._dooray.project.create_tag("proj-1", None, "ff0000")
        with self.assertRaises(AssertionError):
            self._dooray.project.create_tag("proj-1", "bug", None)

    @patch("requests.request")
    def test_get_tag(self, mock_request):
        """Verify endpoint with tag_id and response parsing."""
        mock_request.return_value = self._make_mock_resp(TAG_RESPONSE)

        result = self._dooray.project.get_tag("proj-1", "tag-1")

        call_args = mock_request.call_args
        self.assertIn("/tags/tag-1", call_args[0][1])
        self.assertEqual(result.result.name, "bug")
        self.assertEqual(result.result.color, "ff0000")

    # --- Project > Milestones ---

    @patch("requests.request")
    def test_create_milestone(self, mock_request):
        """Verify body: name, startedAt, endedAt."""
        mock_request.return_value = self._make_mock_resp(RELATION_RESPONSE)

        self._dooray.project.create_milestone("proj-1", "v1.0", "2026-01-01+00:00", "2026-06-30+00:00")

        body = mock_request.call_args.kwargs["json"]
        self.assertEqual(body["name"], "v1.0")
        self.assertEqual(body["startedAt"], "2026-01-01+00:00")
        self.assertEqual(body["endedAt"], "2026-06-30+00:00")

    @patch("requests.request")
    def test_get_milestones_with_status(self, mock_request):
        """Verify query params include status filter."""
        mock_request.return_value = self._make_mock_resp(MILESTONE_LIST_RESPONSE)

        self._dooray.project.get_milestones("proj-1", status="open")

        params = mock_request.call_args.kwargs["params"]
        self.assertEqual(params["status"], "open")

    @patch("requests.request")
    def test_get_milestone(self, mock_request):
        """Verify endpoint with milestone_id."""
        mock_request.return_value = self._make_mock_resp(MILESTONE_RESPONSE)

        result = self._dooray.project.get_milestone("proj-1", "ms-1")

        call_args = mock_request.call_args
        self.assertIn("/milestones/ms-1", call_args[0][1])
        self.assertEqual(result.result.name, "v1.0")

    @patch("requests.request")
    def test_update_milestone(self, mock_request):
        """Verify PUT body: name, status, startedAt, endedAt."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.project.update_milestone("proj-1", "ms-1", "v2.0", "closed", "2026-01-01+00:00", "2026-12-31+00:00")

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "PUT")
        body = call_args.kwargs["json"]
        self.assertEqual(body["name"], "v2.0")
        self.assertEqual(body["status"], "closed")

    @patch("requests.request")
    def test_delete_milestone(self, mock_request):
        """Verify DELETE method is used."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.project.delete_milestone("proj-1", "ms-1")

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "DELETE")
        self.assertIn("/milestones/ms-1", call_args[0][1])

    # --- Project > Hooks ---

    @patch("requests.request")
    def test_create_hook(self, mock_request):
        """Verify body: url, sendEvents."""
        mock_request.return_value = self._make_mock_resp(RELATION_RESPONSE)

        self._dooray.project.create_hook("proj-1", "https://hook.example.com", ["postCreated"])

        body = mock_request.call_args.kwargs["json"]
        self.assertEqual(body["url"], "https://hook.example.com")
        self.assertEqual(body["sendEvents"], ["postCreated"])

    # --- Project > Members ---

    @patch("requests.request")
    def test_add_member(self, mock_request):
        """Verify body: organizationMemberId, role."""
        mock_request.return_value = self._make_mock_resp(PROJECT_MEMBER_RESPONSE)

        result = self._dooray.project.add_member("proj-1", "member-1", "admin")

        body = mock_request.call_args.kwargs["json"]
        self.assertEqual(body["organizationMemberId"], "member-1")
        self.assertEqual(body["role"], "admin")
        self.assertEqual(result.result.organization_member_id, "member-1")

    @patch("requests.request")
    def test_get_member(self, mock_request):
        """Verify endpoint with member_id."""
        mock_request.return_value = self._make_mock_resp(PROJECT_MEMBER_RESPONSE)

        result = self._dooray.project.get_member("proj-1", "member-1")

        call_args = mock_request.call_args
        self.assertIn("/members/member-1", call_args[0][1])
        self.assertEqual(result.result.organization_member_id, "member-1")

    # --- Project > MemberGroups ---

    @patch("requests.request")
    def test_get_member_group(self, mock_request):
        """Verify endpoint with member_group_id."""
        mock_request.return_value = self._make_mock_resp(MEMBER_GROUP_RESPONSE)

        result = self._dooray.project.get_member_group("proj-1", "mg-1")

        call_args = mock_request.call_args
        self.assertIn("/member-groups/mg-1", call_args[0][1])
        self.assertEqual(result.result.id, "mg-1")

    # --- Project > Templates ---

    @patch("requests.request")
    def test_create_template(self, mock_request):
        """Verify to_json_dict() is called on template object."""
        mock_request.return_value = self._make_mock_resp(RELATION_RESPONSE)

        template = dooray.TemplateBuilder()\
            .set_template_name("Test Template")\
            .set_subject("Subject")\
            .create()
        self._dooray.project.create_template("proj-1", template)

        body = mock_request.call_args.kwargs["json"]
        self.assertEqual(body["templateName"], "Test Template")

    @patch("requests.request")
    def test_get_templates(self, mock_request):
        """Verify pagination params."""
        mock_request.return_value = self._make_mock_resp(TEMPLATE_LIST_RESPONSE)

        result = self._dooray.project.get_templates("proj-1", page=1, size=10)

        params = mock_request.call_args.kwargs["params"]
        self.assertEqual(params["page"], 1)
        self.assertEqual(params["size"], 10)
        self.assertEqual(len(result.result), 1)

    @patch("requests.request")
    def test_get_template_with_interpolation(self, mock_request):
        """Verify query param interpolation=true."""
        mock_request.return_value = self._make_mock_resp(TEMPLATE_RESPONSE)

        self._dooray.project.get_template("proj-1", "tmpl-1", interpolation=True)

        params = mock_request.call_args.kwargs["params"]
        self.assertEqual(params["interpolation"], "true")

    @patch("requests.request")
    def test_update_template(self, mock_request):
        """Verify PUT with to_json_dict()."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        template = dooray.TemplateBuilder()\
            .set_template_name("Updated")\
            .create()
        self._dooray.project.update_template("proj-1", "tmpl-1", template)

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "PUT")
        body = call_args.kwargs["json"]
        self.assertEqual(body["templateName"], "Updated")

    @patch("requests.request")
    def test_delete_template(self, mock_request):
        """Verify DELETE method is used."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.project.delete_template("proj-1", "tmpl-1")

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "DELETE")
        self.assertIn("/templates/tmpl-1", call_args[0][1])

    # --- Project > Posts ---

    @patch("requests.request")
    def test_create_post(self, mock_request):
        """Verify to_json_dict() is called on post object."""
        mock_request.return_value = self._make_mock_resp(RELATION_RESPONSE)

        post = dooray.PostBuilder()\
            .set_subject("Test Post")\
            .set_body("Body")\
            .create()
        self._dooray.project.create_post("proj-1", post)

        body = mock_request.call_args.kwargs["json"]
        self.assertEqual(body["subject"], "Test Post")

    @patch("requests.request")
    def test_get_posts_tag_ids_mapping(self, mock_request):
        """P0: tag_ids must map to 'tagIds' query key, not 'ccMemberIds'."""
        mock_request.return_value = self._make_mock_resp(POST_LIST_RESPONSE)

        self._dooray.project.get_posts("proj-1", tag_ids="tag-1")

        params = mock_request.call_args.kwargs["params"]
        self.assertIn("tagIds", params)
        self.assertEqual(params["tagIds"], "tag-1")
        # Ensure tag_ids does NOT leak into ccMemberIds
        if "ccMemberIds" in params:
            self.assertNotEqual(params["ccMemberIds"], "tag-1")

    @patch("requests.request")
    def test_get_posts_filter_params(self, mock_request):
        """Verify all filter params are mapped correctly."""
        mock_request.return_value = self._make_mock_resp(POST_LIST_RESPONSE)

        self._dooray.project.get_posts(
            "proj-1",
            page=1,
            size=50,
            from_email_address="from@test.com",
            from_member_ids="fm-1",
            to_member_ids="tm-1",
            cc_member_ids="cc-1",
            tag_ids="tag-1",
            parent_post_id="pp-1",
            post_workflow_classes="working",
            post_workflow_ids="wf-1",
            milestone_ids="ms-1",
            created_at="today",
            updated_at="thisweek",
            due_at="prev-7d",
            order="-createdAt"
        )

        params = mock_request.call_args.kwargs["params"]
        self.assertEqual(params["page"], 1)
        self.assertEqual(params["size"], 50)
        self.assertEqual(params["fromEmailAddress"], "from@test.com")
        self.assertEqual(params["fromMemberIds"], "fm-1")
        self.assertEqual(params["toMemberIds"], "tm-1")
        self.assertEqual(params["ccMemberIds"], "cc-1")
        self.assertEqual(params["tagIds"], "tag-1")
        self.assertEqual(params["parentPostId"], "pp-1")
        self.assertEqual(params["postWorkflowClasses"], "working")
        self.assertEqual(params["postWorkflowIds"], "wf-1")
        self.assertEqual(params["milestoneIds"], "ms-1")
        self.assertEqual(params["createdAt"], "today")
        self.assertEqual(params["updatedAt"], "thisweek")
        self.assertEqual(params["dueAt"], "prev-7d")
        self.assertEqual(params["order"], "-createdAt")

    @patch("requests.request")
    def test_get_post(self, mock_request):
        """Verify endpoint with post_id."""
        mock_request.return_value = self._make_mock_resp(POST_RESPONSE)

        result = self._dooray.project.get_post("proj-1", "post-1")

        call_args = mock_request.call_args
        self.assertIn("/posts/post-1", call_args[0][1])
        self.assertEqual(result.result.subject, "Test Post")

    @patch("requests.request")
    def test_update_post(self, mock_request):
        """Verify PUT with to_json_dict()."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        post = dooray.PostBuilder()\
            .set_subject("Updated")\
            .set_body("Updated body")\
            .create()
        self._dooray.project.update_post("proj-1", "post-1", post)

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "PUT")

    @patch("requests.request")
    def test_set_post_workflow_for_member(self, mock_request):
        """Verify endpoint with member_id and body with workflowId."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.project.set_post_workflow_for_member("proj-1", "post-1", "member-1", "wf-2")

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "PUT")
        self.assertIn("/posts/post-1/to/member-1", call_args[0][1])
        body = call_args.kwargs["json"]
        self.assertEqual(body["workflowId"], "wf-2")

    @patch("requests.request")
    def test_set_post_workflow(self, mock_request):
        """Verify POST set-workflow endpoint."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.project.set_post_workflow("proj-1", "post-1", "wf-3")

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "POST")
        self.assertIn("/posts/post-1/set-workflow", call_args[0][1])
        body = call_args.kwargs["json"]
        self.assertEqual(body["workflowId"], "wf-3")

    @patch("requests.request")
    def test_set_post_as_done(self, mock_request):
        """Verify POST set-done endpoint."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.project.set_post_as_done("proj-1", "post-1")

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "POST")
        self.assertIn("/posts/post-1/set-done", call_args[0][1])

    # --- Project > Post Logs ---

    @patch("requests.request")
    def test_create_post_log(self, mock_request):
        """Verify body with mimeType=text/x-markdown."""
        mock_request.return_value = self._make_mock_resp(RELATION_RESPONSE)

        self._dooray.project.create_post_log("proj-1", "post-1", "Comment text")

        body = mock_request.call_args.kwargs["json"]
        self.assertEqual(body["body"]["content"], "Comment text")
        self.assertEqual(body["body"]["mimeType"], "text/x-markdown")

    @patch("requests.request")
    def test_get_post_logs(self, mock_request):
        """Verify pagination and order params."""
        mock_request.return_value = self._make_mock_resp(POST_LOG_LIST_RESPONSE)

        self._dooray.project.get_post_logs("proj-1", "post-1", page=0, size=10, order="-createdAt")

        params = mock_request.call_args.kwargs["params"]
        self.assertEqual(params["page"], 0)
        self.assertEqual(params["size"], 10)
        self.assertEqual(params["order"], "-createdAt")

    @patch("requests.request")
    def test_get_post_log(self, mock_request):
        """Verify endpoint with log_id."""
        mock_request.return_value = self._make_mock_resp(POST_LOG_RESPONSE)

        result = self._dooray.project.get_post_log("proj-1", "post-1", "log-1")

        call_args = mock_request.call_args
        self.assertIn("/logs/log-1", call_args[0][1])
        self.assertEqual(result.result.id, "log-1")

    @patch("requests.request")
    def test_update_post_log(self, mock_request):
        """Verify PUT body with content."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.project.update_post_log("proj-1", "post-1", "log-1", "Updated comment")

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "PUT")
        body = call_args.kwargs["json"]
        self.assertEqual(body["body"]["content"], "Updated comment")

    @patch("requests.request")
    def test_delete_post_log(self, mock_request):
        """Verify DELETE method is used."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.project.delete_post_log("proj-1", "post-1", "log-1")

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "DELETE")
        self.assertIn("/logs/log-1", call_args[0][1])
