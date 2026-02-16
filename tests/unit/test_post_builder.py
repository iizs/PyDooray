import unittest
import dooray


class TestPostBuilder(unittest.TestCase):
    def test_minimal_post(self):
        """Subject + body only produces valid JSON."""
        post = dooray.PostBuilder()\
            .set_subject("Test")\
            .set_body("Body text")\
            .create()
        d = post.to_json_dict()

        self.assertEqual(d["subject"], "Test")
        self.assertEqual(d["body"]["content"], "Body text")
        self.assertEqual(d["body"]["mimeType"], "text/x-markdown")

    def test_full_post(self):
        """All fields set produces complete JSON."""
        post = dooray.PostBuilder()\
            .set_subject("Full Post")\
            .set_body("Full body")\
            .set_due_date("2026-12-31")\
            .set_milestone_id("ms-1")\
            .set_priority("high")\
            .set_version("v1")\
            .set_parent_post_id("parent-1")\
            .add_tag_id("tag-1")\
            .add_tag_id("tag-2")\
            .add_to_member("member-1")\
            .add_cc_member("cc-1")\
            .create()
        d = post.to_json_dict()

        self.assertEqual(d["subject"], "Full Post")
        self.assertEqual(d["dueDate"], "2026-12-31")
        self.assertEqual(d["milestoneId"], "ms-1")
        self.assertEqual(d["priority"], "high")
        self.assertEqual(d["version"], "v1")
        self.assertEqual(d["parentPostId"], "parent-1")
        self.assertEqual(d["tagIds"], ["tag-1", "tag-2"])

    def test_add_to_member(self):
        """PostUsers.to is populated with member type."""
        post = dooray.PostBuilder()\
            .set_subject("Test")\
            .add_to_member("member-1")\
            .create()
        d = post.to_json_dict()

        to_list = d["users"]["to"]
        self.assertEqual(len(to_list), 1)
        self.assertEqual(to_list[0]["type"], "member")
        self.assertEqual(to_list[0]["member"]["organizationMemberId"], "member-1")

    def test_add_to_email_user(self):
        """PostUsers.to is populated with emailUser type."""
        post = dooray.PostBuilder()\
            .set_subject("Test")\
            .add_to_email_user("test@example.com", "Test User")\
            .create()
        d = post.to_json_dict()

        to_list = d["users"]["to"]
        self.assertEqual(len(to_list), 1)
        self.assertEqual(to_list[0]["type"], "emailUser")
        self.assertEqual(to_list[0]["emailUser"]["emailAddress"], "test@example.com")
        self.assertEqual(to_list[0]["emailUser"]["name"], "Test User")

    def test_add_cc_member(self):
        """PostUsers.cc is populated correctly."""
        post = dooray.PostBuilder()\
            .set_subject("Test")\
            .add_cc_member("cc-1")\
            .create()
        d = post.to_json_dict()

        cc_list = d["users"]["cc"]
        self.assertEqual(len(cc_list), 1)
        self.assertEqual(cc_list[0]["type"], "member")
        self.assertEqual(cc_list[0]["member"]["organizationMemberId"], "cc-1")

    def test_add_cc_email_user(self):
        """PostUsers.cc is populated with emailUser type."""
        post = dooray.PostBuilder()\
            .set_subject("Test")\
            .add_cc_email_user("cc@example.com", "CC User")\
            .create()
        d = post.to_json_dict()

        cc_list = d["users"]["cc"]
        self.assertEqual(len(cc_list), 1)
        self.assertEqual(cc_list[0]["type"], "emailUser")

    def test_add_multiple_tags(self):
        """tag_ids accumulate with repeated add_tag_id calls."""
        post = dooray.PostBuilder()\
            .set_subject("Test")\
            .add_tag_id("tag-1")\
            .add_tag_id("tag-2")\
            .add_tag_id("tag-3")\
            .create()
        d = post.to_json_dict()

        self.assertEqual(d["tagIds"], ["tag-1", "tag-2", "tag-3"])

    def test_to_json_dict_camel_case(self):
        """Output keys use camelCase."""
        post = dooray.PostBuilder()\
            .set_subject("Test")\
            .set_due_date("2026-01-01")\
            .set_milestone_id("ms-1")\
            .set_parent_post_id("p-1")\
            .create()
        d = post.to_json_dict()

        self.assertIn("dueDate", d)
        self.assertIn("milestoneId", d)
        self.assertIn("parentPostId", d)
        # Verify snake_case keys are NOT present
        self.assertNotIn("due_date", d)
        self.assertNotIn("milestone_id", d)
        self.assertNotIn("parent_post_id", d)

    def test_to_json_dict_omits_none(self):
        """None fields are excluded from JSON output."""
        post = dooray.PostBuilder()\
            .set_subject("Test")\
            .create()
        d = post.to_json_dict()

        self.assertIn("subject", d)
        self.assertNotIn("dueDate", d)
        self.assertNotIn("milestoneId", d)
        self.assertNotIn("priority", d)
        self.assertNotIn("version", d)
        self.assertNotIn("parentPostId", d)
