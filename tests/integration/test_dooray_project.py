"""Integration tests for DoorayProject.

Requires a valid API token and Dooray account.
Pure pytest functions with module-scoped fixtures.
"""
import time
import pytest
import dooray
from dooray.DoorayExceptions import BadHttpResponseStatusCode, ServerGeneralError
from tests.integration.conftest import get_random_member

pytestmark = pytest.mark.integration


# --- Project ---

def test_project_get(dooray_client, project_id):
    project_get = dooray_client.project.get(project_id)
    assert project_get.result.code is not None


def test_project_is_creatable(dooray_client, project_id):
    project_get = dooray_client.project.get(project_id)
    assert dooray_client.project.is_creatable(project_get.result.code) is False
    assert dooray_client.project.is_creatable(project_get.result.code + '-1') is True


# --- Workflows ---

def test_workflows(dooray_client, project_id):
    workflow = dooray_client.project.get_workflows(project_id)
    assert len(workflow.result) > 0


# --- Email (skipped - no delete API) ---

@pytest.mark.skip(reason="Dooray API does not provide email address deletion")
def test_project_email(dooray_client, project_id):
    ts = int(time.time())
    email_create = dooray_client.project.create_email_address(
        project_id,
        f'pydooray.{ts}@pydooray.dooray.com',
        f'PyDooray.{ts}'
    )
    email_get = dooray_client.project.get_email_address(project_id, email_create.result.id)
    assert email_get.result.email_address == f'pydooray.{ts}@pydooray.dooray.com'
    assert email_get.result.name == f'PyDooray.{ts}'


# --- Tags (skipped - no delete API) ---

@pytest.mark.skip(reason="Dooray API does not provide tag deletion")
def test_project_tags(dooray_client, project_id):
    ts = int(time.time())
    tag_create = dooray_client.project.create_tag(project_id, f'tag.{ts}', 'ff0000')
    tag_get = dooray_client.project.get_tag(project_id, tag_create.result.id)
    assert tag_get.result.name == f'tag.{ts}'


# --- Milestones ---

def test_milestone_lifecycle(dooray_client, project_id):
    ts = int(time.time())

    milestone_create = dooray_client.project.create_milestone(
        project_id, f'ms.{ts}', '2021-12-01-08:00', '2021-12-31-08:00'
    )
    milestone_get = dooray_client.project.get_milestone(project_id, milestone_create.result.id)
    assert milestone_get.result.name == f'ms.{ts}'

    dooray_client.project.update_milestone(
        project_id, milestone_create.result.id,
        f'ms2.{ts}', 'open', '2021-11-01-08:00', '2021-11-30-08:00'
    )
    milestone_get = dooray_client.project.get_milestone(project_id, milestone_create.result.id)
    assert milestone_get.result.name == f'ms2.{ts}'

    dooray_client.project.update_milestone(
        project_id, milestone_create.result.id,
        f'ms2.{ts}', 'closed', '2021-11-01-08:00', '2021-11-30-08:00'
    )
    milestone_get = dooray_client.project.get_milestone(project_id, milestone_create.result.id)
    assert milestone_get.result.status == 'closed'

    milestones_get = dooray_client.project.get_milestones(project_id, status='open')
    assert milestones_get is not None

    dooray_client.project.delete_milestone(project_id, milestone_create.result.id)
    with pytest.raises((BadHttpResponseStatusCode, ServerGeneralError)):
        dooray_client.project.get_milestone(project_id, milestone_create.result.id)


# --- Hooks (skipped - no delete API) ---

@pytest.mark.skip(reason="Dooray API does not provide hook deletion")
def test_project_hook(dooray_client, project_id):
    ts = int(time.time())
    hook_create = dooray_client.project.create_hook(
        project_id,
        f'https://test.pydooray.net/hook/{ts}',
        ["postCreated", "postCommentCreated"]
    )
    assert hook_create is not None


# --- Members ---

def test_member_add_and_get(dooray_client, project_id, test_member):
    member_add = dooray_client.project.add_member(project_id, test_member.id, "member")
    assert test_member.id == member_add.result.organization_member_id

    member_get = dooray_client.project.get_member(project_id, test_member.id)
    assert test_member.id == member_get.result.organization_member_id


# --- Member Groups ---

def test_member_group_get(dooray_client, project_id):
    # TODO: member_group_id is hardcoded; may need updating for new projects
    member_group_get = dooray_client.project.get_member_group(project_id, '3172006893474626325')
    assert member_group_get is not None


# --- Templates ---

def test_template_lifecycle(dooray_client, project_id):
    ts = int(time.time())
    to_member = get_random_member(dooray_client)
    cc_member_1 = get_random_member(dooray_client)
    cc_member_2 = get_random_member(dooray_client)

    templates_get = dooray_client.project.get_templates(project_id)
    count_templates = templates_get.total_count

    template_builder = dooray.TemplateBuilder()
    template = template_builder\
        .set_template_name(f'Template {ts}')\
        .add_to_member(to_member.id)\
        .add_cc_member(cc_member_1.id)\
        .set_body(f'Body {ts}')\
        .set_subject(f'Template {ts} - ${{year}}')\
        .create()
    template_create = dooray_client.project.create_template(project_id, template)
    assert template_create.result.id is not None

    template_get = dooray_client.project.get_template(project_id, template_create.result.id)
    assert template_get is not None

    template_get = dooray_client.project.get_template(
        project_id, template_create.result.id, interpolation=True
    )
    assert template_get is not None

    templates_get = dooray_client.project.get_templates(project_id)
    assert templates_get.total_count == count_templates + 1

    template = template_builder.add_cc_member(cc_member_2.id).create()
    dooray_client.project.update_template(project_id, template_create.result.id, template)

    template_get = dooray_client.project.get_template(project_id, template_create.result.id)
    assert template_get is not None

    dooray_client.project.delete_template(project_id, template_create.result.id)

    templates_get = dooray_client.project.get_templates(project_id)
    assert templates_get.total_count == count_templates


# --- Posts ---

def test_post_create_and_get(dooray_client, project_id):
    ts = int(time.time())
    to_member = get_random_member(dooray_client)
    cc_member = get_random_member(dooray_client)

    post_builder = dooray.PostBuilder()
    post = post_builder\
        .add_to_member(to_member.id)\
        .add_cc_member(cc_member.id)\
        .set_body(f'Body {ts}')\
        .set_subject(f'Post {ts}')\
        .create()
    post_create = dooray_client.project.create_post(project_id, post)
    assert post_create.result.id is not None

    post_get = dooray_client.project.get_post(project_id, post_create.result.id)
    assert post_get.result.subject is not None


def test_post_update(dooray_client, project_id):
    ts = int(time.time())
    to_member = get_random_member(dooray_client)

    post_builder = dooray.PostBuilder()
    post = post_builder\
        .add_to_member(to_member.id)\
        .set_body(f'Body {ts}')\
        .set_subject(f'Post {ts}')\
        .create()
    post_create = dooray_client.project.create_post(project_id, post)

    time.sleep(0.1)

    post_update = post_builder\
        .set_subject(f'Post {ts} - updated')\
        .set_body(f'Body {ts} - updated')\
        .create()
    dooray_client.project.update_post(project_id, post_create.result.id, post_update)


def test_post_filter_by_to_member(dooray_client, project_id):
    ts = int(time.time())
    to_member = get_random_member(dooray_client)

    post_builder = dooray.PostBuilder()
    post = post_builder\
        .add_to_member(to_member.id)\
        .set_body(f'Body filter test {ts}')\
        .set_subject(f'Post filter test {ts}')\
        .create()
    dooray_client.project.create_post(project_id, post)

    time.sleep(0.5)

    posts_get = dooray_client.project.get_posts(project_id, to_member_ids=to_member.id)
    for p in posts_get.result:
        found = any(
            u.type == 'member' and u.member.organization_member_id == to_member.id
            for u in p.users.to
        )
        assert found


def test_post_workflow_operations(dooray_client, project_id):
    ts = int(time.time())
    to_member = get_random_member(dooray_client)

    post_builder = dooray.PostBuilder()
    post = post_builder\
        .add_to_member(to_member.id)\
        .set_body(f'Body wf {ts}')\
        .set_subject(f'Post wf {ts}')\
        .create()
    post_create = dooray_client.project.create_post(project_id, post)

    workflow = dooray_client.project.get_workflows(project_id)
    workflows = {w.workflow_class: w for w in workflow.result}

    dooray_client.project.set_post_workflow_for_member(
        project_id, post_create.result.id, to_member.id, workflows['working'].id
    )

    dooray_client.project.set_post_workflow(
        project_id, post_create.result.id, workflows['working'].id
    )

    dooray_client.project.set_post_as_done(project_id, post_create.result.id)


def test_post_log_lifecycle(dooray_client, project_id):
    ts = int(time.time())
    to_member = get_random_member(dooray_client)

    post_builder = dooray.PostBuilder()
    post = post_builder\
        .add_to_member(to_member.id)\
        .set_body(f'Body log {ts}')\
        .set_subject(f'Post log {ts}')\
        .create()
    post_create = dooray_client.project.create_post(project_id, post)

    log_1 = dooray_client.project.create_post_log(
        project_id, post_create.result.id, 'First Comment with markdown'
    )
    assert log_1.result.id is not None

    time.sleep(0.1)

    log_2 = dooray_client.project.create_post_log(
        project_id, post_create.result.id, 'Second Comment with markdown'
    )
    assert log_2.result.id is not None

    post_logs_get = dooray_client.project.get_post_logs(project_id, post_create.result.id)
    assert len(post_logs_get.result) > 0

    post_log_get = dooray_client.project.get_post_log(
        project_id, post_create.result.id, log_1.result.id
    )
    assert post_log_get.result.id is not None

    dooray_client.project.update_post_log(
        project_id, post_create.result.id, log_1.result.id,
        'First Comment with markdown - updated'
    )

    post_log_get = dooray_client.project.get_post_log(
        project_id, post_create.result.id, log_1.result.id
    )
    assert post_log_get.result.body.content == 'First Comment with markdown - updated'

    dooray_client.project.delete_post_log(project_id, post_create.result.id, log_1.result.id)
    dooray_client.project.delete_post_log(project_id, post_create.result.id, log_2.result.id)

    post_logs_get = dooray_client.project.get_post_logs(project_id, post_create.result.id)
    assert post_logs_get.result == []
