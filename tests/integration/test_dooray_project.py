"""Integration tests for DoorayProject.

Refactored from tests/test_DoorayProject.py.
Requires a valid API token and Dooray account.
"""
import unittest
import time
import random
import pytest
import dooray
from dooray.DoorayExceptions import BadHttpResponseStatusCode, ServerGeneralError
from tests.tokens import API_TOKEN

MEMBER_ID_FOR_TEST = '2492022087928904640'


@pytest.mark.integration
class TestDoorayProject(unittest.TestCase):
    def setUp(self):
        self._dooray = dooray.Dooray(API_TOKEN)
        self._ts = int(time.time())
        self._project_id = 3172006893461634976

        if self._project_id is None:
            project_name = f'PyDooray-{str(self._ts)}'
            project_desc = f'Created by PyDooray > TestDoorayProject at {str(self._ts)}'
            project_scope = 'private'
            project = self._dooray.project.create(project_name, project_desc, project_scope)
            self._project_id = project.result.id

    def tearDown(self):
        time.sleep(0.5)

    def get_test_member(self, seed=None):
        if seed is not None:
            random.seed(self._ts)
        members = self._dooray.get_members(user_code='')
        idx = random.randint(0, min(members.total_count, members.size) - 1)
        return members.result[idx]

    # --- Project ---

    def test_project_get(self):
        project_get = self._dooray.project.get(self._project_id)
        self.assertIsNotNone(project_get.result.code)

    def test_project_is_creatable(self):
        project_get = self._dooray.project.get(self._project_id)
        self.assertFalse(self._dooray.project.is_creatable(project_get.result.code))
        self.assertTrue(self._dooray.project.is_creatable(project_get.result.code + '-1'))

    # --- Workflows ---

    def test_workflows(self):
        workflow = self._dooray.project.get_workflows(self._project_id)
        self.assertGreater(len(workflow.result), 0)

    # --- Email (skipped - no delete API) ---

    @unittest.skip("Skip test until Email deletion API provided")
    def test_project_email(self):
        email_create = self._dooray.project.create_email_address(
            self._project_id,
            f'pydooray.{str(self._ts)}@pydooray.dooray.com',
            f'PyDooray.{str(self._ts)}'
        )
        email_get = self._dooray.project.get_email_address(self._project_id, email_create.result.id)
        self.assertEqual(email_get.result.email_address, f'pydooray.{str(self._ts)}@pydooray.dooray.com')
        self.assertEqual(email_get.result.name, f'PyDooray.{str(self._ts)}')

    # --- Tags (skipped - no delete API) ---

    @unittest.skip("Skip test until Tag deletion API provided")
    def test_project_tags(self):
        tag_create = self._dooray.project.create_tag(self._project_id, f'tag.{str(self._ts)}', 'ff0000')
        tag_get = self._dooray.project.get_tag(self._project_id, tag_create.result.id)
        self.assertEqual(tag_get.result.name, f'tag.{str(self._ts)}')

    # --- Milestones ---

    def test_milestone_lifecycle(self):
        milestone_create = self._dooray.project.create_milestone(
            self._project_id,
            f'ms.{str(self._ts)}',
            '2021-12-01-08:00',
            '2021-12-31-08:00'
        )
        milestone_get = self._dooray.project.get_milestone(self._project_id, milestone_create.result.id)
        self.assertEqual(milestone_get.result.name, f'ms.{str(self._ts)}')

        self._dooray.project.update_milestone(
            self._project_id,
            milestone_create.result.id,
            f'ms2.{str(self._ts)}',
            'open',
            '2021-11-01-08:00',
            '2021-11-30-08:00'
        )
        milestone_get = self._dooray.project.get_milestone(self._project_id, milestone_create.result.id)
        self.assertEqual(milestone_get.result.name, f'ms2.{str(self._ts)}')

        self._dooray.project.update_milestone(
            self._project_id,
            milestone_create.result.id,
            f'ms2.{str(self._ts)}',
            'closed',
            '2021-11-01-08:00',
            '2021-11-30-08:00'
        )
        milestone_get = self._dooray.project.get_milestone(self._project_id, milestone_create.result.id)
        self.assertEqual(milestone_get.result.status, 'closed')

        milestones_get = self._dooray.project.get_milestones(self._project_id, status='open')
        self.assertIsNotNone(milestones_get)

        self._dooray.project.delete_milestone(self._project_id, milestone_create.result.id)
        with self.assertRaises((BadHttpResponseStatusCode, ServerGeneralError)):
            self._dooray.project.get_milestone(self._project_id, milestone_create.result.id)

    # --- Hooks (skipped - no delete API) ---

    @unittest.skip("Skip test until Hook deletion API provided")
    def test_project_hook(self):
        hook_create = self._dooray.project.create_hook(
            self._project_id,
            f'https://test.pydooray.net/hook/{str(self._ts)}',
            ["postCreated", "postCommentCreated"]
        )
        self.assertIsNotNone(hook_create)

    # --- Members ---

    def test_member_add_and_get(self):
        test_member = self.get_test_member()
        self.assertIsNotNone(test_member)

        member_add = self._dooray.project.add_member(self._project_id, test_member.id, "member")
        self.assertEqual(test_member.id, member_add.result.organization_member_id)

        member_get = self._dooray.project.get_member(self._project_id, test_member.id)
        self.assertEqual(test_member.id, member_get.result.organization_member_id)

    # --- Member Groups ---

    def test_member_group_get(self):
        member_group_get = self._dooray.project.get_member_group(self._project_id, '3172006893474626325')
        self.assertIsNotNone(member_group_get)

    # --- Templates ---

    def test_template_lifecycle(self):
        test_to_member = self.get_test_member()
        test_cc_member_1 = self.get_test_member()
        test_cc_member_2 = self.get_test_member()

        templates_get = self._dooray.project.get_templates(self._project_id)
        count_templates = templates_get.total_count

        template_builder = dooray.TemplateBuilder()
        template = template_builder\
            .set_template_name(f'Template {self._ts}')\
            .add_to_member(test_to_member.id)\
            .add_cc_member(test_cc_member_1.id)\
            .set_body(f'Body {self._ts}')\
            .set_subject(f'Template {self._ts} - ${{year}}')\
            .create()
        template_create = self._dooray.project.create_template(self._project_id, template)
        self.assertIsNotNone(template_create.result.id)

        template_get = self._dooray.project.get_template(self._project_id, template_create.result.id)
        self.assertIsNotNone(template_get)

        template_get = self._dooray.project.get_template(
            self._project_id,
            template_create.result.id,
            interpolation=True
        )
        self.assertIsNotNone(template_get)

        templates_get = self._dooray.project.get_templates(self._project_id)
        self.assertEqual(templates_get.total_count, count_templates + 1)

        template = template_builder.add_cc_member(test_cc_member_2.id).create()
        self._dooray.project.update_template(self._project_id, template_create.result.id, template)

        template_get = self._dooray.project.get_template(self._project_id, template_create.result.id)
        self.assertIsNotNone(template_get)

        self._dooray.project.delete_template(self._project_id, template_create.result.id)

        templates_get = self._dooray.project.get_templates(self._project_id)
        self.assertEqual(templates_get.total_count, count_templates)

    # --- Posts (split from monolithic test_ProjectPost) ---

    def test_post_create_and_get(self):
        """Create a post and verify it can be retrieved."""
        test_to_member = self.get_test_member()
        test_cc_member_1 = self.get_test_member()

        post_builder = dooray.PostBuilder()
        post = post_builder\
            .add_to_member(test_to_member.id)\
            .add_cc_member(test_cc_member_1.id)\
            .set_body(f'Body {self._ts}')\
            .set_subject(f'Post {self._ts}')\
            .create()
        post_create = self._dooray.project.create_post(self._project_id, post)
        self.assertIsNotNone(post_create.result.id)

        post_get = self._dooray.project.get_post(self._project_id, post_create.result.id)
        self.assertIsNotNone(post_get.result.subject)

    def test_post_update(self):
        """Create a post then update it."""
        test_to_member = self.get_test_member()

        post_builder = dooray.PostBuilder()
        post = post_builder\
            .add_to_member(test_to_member.id)\
            .set_body(f'Body {self._ts}')\
            .set_subject(f'Post {self._ts}')\
            .create()
        post_create = self._dooray.project.create_post(self._project_id, post)

        time.sleep(0.1)

        post_update = post_builder\
            .set_subject(f'Post {self._ts} - updated')\
            .set_body(f'Body {self._ts} - updated')\
            .create()
        self._dooray.project.update_post(self._project_id, post_create.result.id, post_update)

    def test_post_filter_by_to_member(self):
        """Create a post and filter by to_member_ids to verify filter works."""
        test_to_member = self.get_test_member()

        post_builder = dooray.PostBuilder()
        post = post_builder\
            .add_to_member(test_to_member.id)\
            .set_body(f'Body filter test {self._ts}')\
            .set_subject(f'Post filter test {self._ts}')\
            .create()
        self._dooray.project.create_post(self._project_id, post)

        time.sleep(0.5)

        posts_get = self._dooray.project.get_posts(
            self._project_id,
            to_member_ids=test_to_member.id
        )
        for post in posts_get.result:
            found = False
            for u in post.users.to:
                if u.type == 'member' and u.member.organization_member_id == test_to_member.id:
                    found = True
                    break
            self.assertTrue(found)

    def test_post_workflow_operations(self):
        """Create a post and exercise workflow state transitions."""
        test_to_member = self.get_test_member()

        post_builder = dooray.PostBuilder()
        post = post_builder\
            .add_to_member(test_to_member.id)\
            .set_body(f'Body wf {self._ts}')\
            .set_subject(f'Post wf {self._ts}')\
            .create()
        post_create = self._dooray.project.create_post(self._project_id, post)

        workflow = self._dooray.project.get_workflows(self._project_id)
        workflows = {}
        for w in workflow.result:
            workflows[w.workflow_class] = w

        self._dooray.project.set_post_workflow_for_member(
            self._project_id,
            post_create.result.id,
            test_to_member.id,
            workflows['working'].id
        )

        self._dooray.project.set_post_workflow(
            self._project_id,
            post_create.result.id,
            workflows['working'].id
        )

        self._dooray.project.set_post_as_done(self._project_id, post_create.result.id)

    def test_post_log_lifecycle(self):
        """Create a post, add/update/delete logs (comments)."""
        test_to_member = self.get_test_member()

        post_builder = dooray.PostBuilder()
        post = post_builder\
            .add_to_member(test_to_member.id)\
            .set_body(f'Body log {self._ts}')\
            .set_subject(f'Post log {self._ts}')\
            .create()
        post_create = self._dooray.project.create_post(self._project_id, post)

        post_log_create_1 = self._dooray.project.create_post_log(
            self._project_id,
            post_create.result.id,
            'First Comment with markdown'
        )
        self.assertIsNotNone(post_log_create_1.result.id)

        time.sleep(0.1)

        post_log_create_2 = self._dooray.project.create_post_log(
            self._project_id,
            post_create.result.id,
            'Second Comment with markdown'
        )
        self.assertIsNotNone(post_log_create_2.result.id)

        post_logs_get = self._dooray.project.get_post_logs(self._project_id, post_create.result.id)
        self.assertGreater(len(post_logs_get.result), 0)

        post_log_get = self._dooray.project.get_post_log(
            self._project_id,
            post_create.result.id,
            post_log_create_1.result.id
        )
        self.assertIsNotNone(post_log_get.result.id)

        self._dooray.project.update_post_log(
            self._project_id,
            post_create.result.id,
            post_log_create_1.result.id,
            'First Comment with markdown - updated'
        )

        post_log_get = self._dooray.project.get_post_log(
            self._project_id,
            post_create.result.id,
            post_log_create_1.result.id
        )
        self.assertEqual(post_log_get.result.body.content, 'First Comment with markdown - updated')

        self._dooray.project.delete_post_log(
            self._project_id, post_create.result.id, post_log_create_1.result.id
        )
        self._dooray.project.delete_post_log(
            self._project_id, post_create.result.id, post_log_create_2.result.id
        )

        post_logs_get = self._dooray.project.get_post_logs(self._project_id, post_create.result.id)
        self.assertEqual(post_logs_get.result, [])
