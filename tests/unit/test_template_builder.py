import unittest
import dooray


class TestTemplateBuilder(unittest.TestCase):
    def test_minimal_template(self):
        """templateName is always included in JSON output."""
        template = dooray.TemplateBuilder()\
            .set_template_name("Bug Report")\
            .create()
        d = template.to_json_dict()

        self.assertEqual(d["templateName"], "Bug Report")

    def test_full_template(self):
        """All fields set produces complete JSON."""
        template = dooray.TemplateBuilder()\
            .set_template_name("Full Template")\
            .set_subject("Subject")\
            .set_body("Body text")\
            .set_guide("Guide text")\
            .set_due_date("2026-12-31")\
            .set_milestone_id("ms-1")\
            .set_priority("normal")\
            .set_is_default(True)\
            .add_tag_id("tag-1")\
            .add_to_member("member-1")\
            .add_cc_member("cc-1")\
            .create()
        d = template.to_json_dict()

        self.assertEqual(d["templateName"], "Full Template")
        self.assertEqual(d["subject"], "Subject")
        self.assertEqual(d["body"]["content"], "Body text")
        self.assertEqual(d["guide"]["content"], "Guide text")
        self.assertEqual(d["dueDate"], "2026-12-31")
        self.assertEqual(d["milestoneId"], "ms-1")
        self.assertEqual(d["priority"], "normal")
        self.assertTrue(d["isDefault"])
        self.assertEqual(d["tagIds"], ["tag-1"])

    def test_set_guide(self):
        """guide creates PostBody with markdown mimeType."""
        template = dooray.TemplateBuilder()\
            .set_template_name("Test")\
            .set_guide("Fill in the template")\
            .create()
        d = template.to_json_dict()

        self.assertEqual(d["guide"]["mimeType"], "text/x-markdown")
        self.assertEqual(d["guide"]["content"], "Fill in the template")

    def test_set_is_default(self):
        """isDefault boolean is serialized correctly."""
        template_true = dooray.TemplateBuilder()\
            .set_template_name("Default")\
            .set_is_default(True)\
            .create()
        self.assertTrue(template_true.to_json_dict()["isDefault"])

        template_false = dooray.TemplateBuilder()\
            .set_template_name("Not Default")\
            .set_is_default(False)\
            .create()
        self.assertFalse(template_false.to_json_dict()["isDefault"])

    def test_to_json_dict_camel_case(self):
        """Output keys use camelCase."""
        template = dooray.TemplateBuilder()\
            .set_template_name("Test")\
            .set_due_date("2026-01-01")\
            .set_milestone_id("ms-1")\
            .set_is_default(True)\
            .create()
        d = template.to_json_dict()

        self.assertIn("templateName", d)
        self.assertIn("dueDate", d)
        self.assertIn("milestoneId", d)
        self.assertIn("isDefault", d)
        # Verify snake_case keys are NOT present
        self.assertNotIn("template_name", d)
        self.assertNotIn("due_date", d)
        self.assertNotIn("milestone_id", d)
        self.assertNotIn("is_default", d)
