import unittest
import time
import random
import dooray
from dooray.DoorayExceptions import BadHttpResponseStatusCode, ServerGeneralError
from tests.tokens import API_TOKEN

MEMBER_ID_FOR_TEST = '2492022087928904640'


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
        # TODO this might be a hack to get all members. If this is not allowed, need to find out better way.
        members = self._dooray.get_members(user_code='')
        idx = random.randint(0, min(members.total_count, members.size)-1)
        return members.result[idx]

    def test_Project(self):
        project_get = self._dooray.project.get(self._project_id)
        print(project_get)

        self.assertFalse(self._dooray.project.is_creatable(project_get.result.code))
        self.assertTrue(self._dooray.project.is_creatable(project_get.result.code + '-1'))

        workflow = self._dooray.project.get_workflows(self._project_id)
        print(workflow)

    @unittest.skip("Skip test until Email deletion API provided")
    def test_ProjectEmail(self):
        email_create = self._dooray.project.create_email_address(
            self._project_id,
            f'pydooray.{str(self._ts)}@pydooray.dooray.com',
            f'PyDooray.{str(self._ts)}'
        )
        email_get = self._dooray.project.get_email_address(self._project_id, email_create.result.id)
        self.assertEqual(email_get.result.email_address, f'pydooray.{str(self._ts)}@pydooray.dooray.com')
        self.assertEqual(email_get.result.name, f'PyDooray.{str(self._ts)}')
        print(email_get)

    @unittest.skip("Skip test until Tag deletion API provided")
    def test_ProjectTags(self):
        tag_create = self._dooray.project.create_tag(self._project_id, f'tag.{str(self._ts)}', 'ff0000')
        tag_get = self._dooray.project.get_tag(self._project_id, tag_create.result.id)
        self.assertEqual(tag_get.result.name, f'tag.{str(self._ts)}')
        print(tag_get)

    def test_ProjectMilestone(self):
        milestone_create = self._dooray.project.create_milestone(
            self._project_id,
            f'ms.{str(self._ts)}',
            '2021-12-01-08:00',
            '2021-12-31-08:00'
        )
        milestone_get = self._dooray.project.get_milestone(self._project_id, milestone_create.result.id)
        self.assertEqual(milestone_get.result.name, f'ms.{str(self._ts)}')
        print(milestone_get)

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
        print(milestone_get)

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
        print(milestone_get)

        milestones_get = self._dooray.project.get_milestones(self._project_id, status='open')
        print(milestones_get)

        self._dooray.project.delete_milestone(self._project_id, milestone_create.result.id)
        with self.assertRaises((BadHttpResponseStatusCode, ServerGeneralError)) as bad_resp:
            self._dooray.project.get_milestone(self._project_id, milestone_create.result.id)

    @unittest.skip("Skip test until Hook deletion API provided")
    def test_ProjectHook(self):
        hook_create = self._dooray.project.create_hook(
            self._project_id,
            f'https://test.pydooray.net/hook/{str(self._ts)}',
            ["postCreated", "postCommentCreated"]
        )
        print(hook_create)

    def test_ProjectMember(self):
        test_member = self.get_test_member()
        print(test_member)

        member_add = self._dooray.project.add_member(self._project_id, test_member.id, "member")
        print(member_add)
        self.assertEqual(test_member.id, member_add.result.organization_member_id)

        member_get = self._dooray.project.get_member(self._project_id, test_member.id)
        print(member_get)
        self.assertEqual(test_member.id, member_get.result.organization_member_id)

    def test_ProjectMemberGroup(self):
        # TODO below test is commented out due to API error
        #member_groups_get = self._dooray.project.get_member_groups(self._project_id)

        member_group_get = self._dooray.project.get_member_group(self._project_id, '3172006893474626325')
        print(member_group_get)

    def test_ProjectTemplate(self):
        test_to_member = self.get_test_member()
        print(test_to_member)
        test_cc_member_1 = self.get_test_member()
        print(test_cc_member_1)
        test_cc_member_2 = self.get_test_member()
        print(test_cc_member_2)

        templates_get = self._dooray.project.get_templates(self._project_id)
        print(templates_get)
        count_templates = templates_get.total_count

        template_builder = dooray.TemplateBuilder()
        template = template_builder\
            .set_template_name(f'Template {self._ts}')\
            .add_to_member(test_to_member.id)\
            .add_cc_member(test_cc_member_1.id)\
            .set_body(f'Body {self._ts}')\
            .set_subject(f'Template {self._ts} - ${{year}}')\
            .create()
        print(template.to_json_dict())
        template_create = self._dooray.project.create_template(self._project_id, template)
        print(template_create)

        template_get = self._dooray.project.get_template(self._project_id, template_create.result.id)
        print(template_get)

        template_get = self._dooray.project.get_template(
            self._project_id,
            template_create.result.id,
            interpolation=True
        )
        print(template_get)

        templates_get = self._dooray.project.get_templates(self._project_id)
        print(templates_get)
        self.assertEqual(templates_get.total_count, count_templates + 1)

        template = template_builder.add_cc_member(test_cc_member_2.id).create()
        self._dooray.project.update_template(self._project_id, template_create.result.id, template)

        template_get = self._dooray.project.get_template(self._project_id, template_create.result.id)
        print(template_get)

        self._dooray.project.delete_template(self._project_id, template_create.result.id)

        templates_get = self._dooray.project.get_templates(self._project_id)
        print(templates_get)
        self.assertEqual(templates_get.total_count, count_templates)

    def test_ProjectPost(self):
        test_to_member = self.get_test_member()
        print(test_to_member)
        test_cc_member_1 = self.get_test_member()
        print(test_cc_member_1)
        test_cc_member_2 = self.get_test_member()
        print(test_cc_member_2)

        posts_get = self._dooray.project.get_posts(self._project_id)
        print(posts_get)
        count_posts = posts_get.total_count

        post_builder = dooray.PostBuilder()
        post_1 = post_builder\
            .add_to_member(test_to_member.id)\
            .add_cc_member(test_cc_member_1.id)\
            .set_body(f'Body {self._ts}')\
            .set_subject(f'Post {self._ts}')\
            .create()
        print(post_1.to_json_dict())
        post_create_1 = self._dooray.project.create_post(self._project_id, post_1)
        print(post_create_1)

        post_2 = post_builder\
            .set_parent_post_id(post_create_1.result.id) \
            .set_subject(f'Post {self._ts} - child of {post_create_1.result.id}') \
            .set_body(f'Body {self._ts} - child of {post_create_1.result.id}')\
            .add_cc_member(test_cc_member_2.id)\
            .create()
        print(post_2.to_json_dict())
        post_create_2 = self._dooray.project.create_post(self._project_id, post_2)
        print(post_create_2)

        post_get_1 = self._dooray.project.get_post(self._project_id, post_create_1.result.id)
        print(post_get_1)
        post_get_2 = self._dooray.project.get_post(self._project_id, post_create_2.result.id)
        print(post_get_2)

        posts_get = self._dooray.project.get_posts(
            self._project_id,
            to_member_ids=test_to_member.id
        )
        print(posts_get)
        for post in posts_get.result:
            found = False
            for u in post.users.to:
                if u.type == 'member' and u.member.organization_member_id == test_to_member.id:
                    found = True
                    break
            self.assertTrue(found)

        post_2_update = post_builder \
            .set_parent_post_id(post_create_1.result.id) \
            .set_subject(f'Post {self._ts} - child of {post_create_1.result.id} - updated') \
            .set_body(f'Body {self._ts} - child of {post_create_1.result.id} - updated') \
            .create()

        post_update = self._dooray.project.update_post(self._project_id, post_create_2.result.id, post_2_update)
        print(post_update)

        workflow = self._dooray.project.get_workflows(self._project_id)
        print(workflow)
        workflows = {}
        for w in workflow.result:
            workflows[w.workflow_class] = w

        self._dooray.project.set_post_workflow_for_member(
            self._project_id,
            post_create_2.result.id,
            test_to_member.id,
            workflows['working'].id
        )

        self._dooray.project.set_post_workflow(self._project_id, post_create_1.result.id, workflows['working'].id)

        self._dooray.project.set_post_as_done(self._project_id, post_create_1.result.id)

        post_log_create_1 = self._dooray.project.create_post_log(
            self._project_id,
            post_create_1.result.id,
            'First Comment with markdown'
        )
        print(post_log_create_1)

        time.sleep(0.1)

        post_log_create_2 = self._dooray.project.create_post_log(
            self._project_id,
            post_create_1.result.id,
            'Second Comment with markdown'
        )
        print(post_log_create_2)

        post_logs_get = self._dooray.project.get_post_logs(self._project_id, post_create_1.result.id)
        print(post_logs_get)

        post_log_get = self._dooray.project.get_post_log(
            self._project_id,
            post_create_1.result.id,
            post_log_create_1.result.id
        )
        print(post_log_get)

        self._dooray.project.update_post_log(
            self._project_id,
            post_create_1.result.id,
            post_log_create_1.result.id,
            'First Comment with markdown - updated'
        )

        post_log_get = self._dooray.project.get_post_log(
            self._project_id,
            post_create_1.result.id,
            post_log_create_1.result.id
        )
        print(post_log_get)
        self.assertEqual(post_log_get.result.body.content, 'First Comment with markdown - updated')

        self._dooray.project.delete_post_log(self._project_id, post_create_1.result.id, post_log_create_1.result.id)
        self._dooray.project.delete_post_log(self._project_id, post_create_1.result.id, post_log_create_2.result.id)

        post_logs_get = self._dooray.project.get_post_logs(self._project_id, post_create_1.result.id)
        print(post_logs_get)
        self.assertEqual(post_logs_get.result, [])
