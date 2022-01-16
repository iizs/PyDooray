import dooray.DoorayObjects
from dooray.Member import Member


class Project:
    def __init__(self, data):
        self.id = data['id']
        """"""
        self.code = data['code']
        """"""
        self.description = None if 'description' not in data else data['description']
        """"""
        self.scope = None if 'scope' not in data else data['scope']
        """"""
        self.state = None if 'state' not in data else data['state']
        """"""
        self.type = None if 'type' not in data else data['type']
        """"""
        self.organization = None if 'organization' not in data else dooray.DoorayObjects.Relation(data['organization'])
        """
        :type: :class:`dooray.DoorayObjects.Relation`
        """
        self.wiki = None if 'wiki' not in data else dooray.DoorayObjects.Relation(data['wiki'])
        """
        :type: :class:`dooray.DoorayObjects.Relation`
        """
        self.drive = None if 'drive' not in data else dooray.DoorayObjects.Relation(data['drive'])
        """
        :type: :class:`dooray.DoorayObjects.Relation`
        """
        # { state, type, organization, wiki, drive } are un-documented

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'code': '{self.code}', 'description': '{self.description}', " \
               f"'state': '{self.state}', 'type': '{self.type}', 'scope': '{self.scope}', " \
               f"'organization': '{self.organization}', 'wiki': '{self.wiki}', 'drive': {self.drive} }}"


class DisplayName:
    def __init__(self, data):
        self.locale = data['locale']
        """"""
        self.name = data['name']
        """"""

    def __repr__(self):
        return f"{{ 'locale': '{self.locale}', 'name': '{self.name}' }}"


class Workflow:
    def __init__(self, data):
        self.id = data['id']
        """"""
        self.name = data['name']
        """"""
        self.order = data['order'] if 'order' in data else None
        """"""
        self.workflow_class = data['class'] if 'class' in data else None
        """"""
        self.names = []
        """"""
        if 'names' in data:
            for e in data['names']:
                self.names.append(DisplayName(e))

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'order': '{self.order}', " \
               f"'workflow_class': '{self.workflow_class}', 'names': '{[e for e in self.names]}' }}"


class EmailAddress:
    def __init__(self, data):
        self.id = data['id'] if 'id' in data else None
        """"""
        self.name = data['name']
        """"""
        self.email_address = data['emailAddress']
        """"""

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'email_address': '{self.email_address}' }}"

    def to_json_dict(self):
        d = {
            'name': self.name,
            'emailAddress': self.email_address
        }
        if self.id is not None:
            d['id'] = self.id
        return d


class Tag:
    def __init__(self, data):
        self.id = data['id']
        """"""
        self.name = data['name'] if 'name' in data else None
        """"""
        self.color = data['color'] if 'color' in data else None
        """
        The color of the tag in hexadecimal format. Example: `00ff00`
        """

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'color': '{self.color}' }}"


class Milestone:
    def __init__(self, data):
        self.id = data['id']
        """"""
        self.name = data['name']
        """"""
        self.status = data['status'] if 'status' in data else None
        """
        The status of the milestone. Possible values are `open` and `closed`.
        """
        # Milestone without a period do not return 'startedAt' and 'endAt' field.
        self.started_at = data['startedAt'] if 'startedAt' in data else None
        """"""
        self.ended_at = data['endedAt'] if 'endedAt' in data else None
        """"""
        self.closed_at = data['closedAt'] if 'closedAt' in data else None
        """"""
        self.created_at = data['createdAt'] if 'createdAt' in data else None
        """"""
        self.updated_at = data['updatedAt'] if 'updatedAt' in data else None
        """"""

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'status': '{self.status}', " \
               f"'started_at': '{self.started_at}', 'ended_at': '{self.ended_at}', " \
               f"'closed_at': '{self.closed_at}', 'created_at': '{self.created_at}', " \
               f"'updated_at': '{self.updated_at}'}}"


class ProjectMember:
    def __init__(self, data):
        self.organization_member_id = data['organizationMemberId']
        """"""
        self.role = data['role'] if 'role' in data else None
        """"""

    def __repr__(self):
        return f"{{ 'organizationMemberId': '{self.organization_member_id}', 'role': '{self.role}' }}"

    def to_json_dict(self):
        d = {'organizationMemberId': self.organization_member_id}
        if self.role is not None:
            d['role'] = self.role
        return d


class MemberGroup:
    def __init__(self, data):
        self.id = data['id']
        """"""
        self.code = data['code']
        """"""
        self.created_at = data['createdAt']
        """"""
        self.updated_at = data['updatedAt']
        """"""
        self.project = Project(data['project'])
        """
        :type: :class:`dooray.Project.Project`
        """
        if 'members' in data:
            self.members = [MemberGroupMember(e) for e in data['members']]
            """
            :type: list of :class:`dooray.MemberGroup.MemberGroupMember`
            """

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'code': '{self.code}', " \
               f"'created_at': '{self.created_at}', 'updated_at': '{self.updated_at}', " \
               f"'project': '{self.project}', 'members': {self.members} }}"


class MemberGroupMember:
    def __init__(self, data):
        self.organization_member = Member(data)
        """
        :type: :class:`dooray.Member.Member`
        """

    def __repr__(self):
        return f"{self.organization_member}"


class BasePost:
    def __init__(self, data=None):
        if data is not None:
            self.users = PostUsers(data['users']) if 'users' in data else None
            """
            :type: :class:`dooray.Project.PostUsers`
            """
            self.body = PostBody(data['body']) if 'body' in data else None
            """
            :type: :class:`dooray.Project.PostBody`
            """
            self.subject = data['subject']
            """
            The subject of the post or the template.
            """
            self.due_date = data['dueDate'] if 'dueDate' in data else None
            """
            The due date of the post or the template.
            """
            # TODO: dueDateFlag is marked as deprecated from the post document but not in the template document.
            #  Which is correct?
            self.due_date_flag = data['dueDateFlag'] if 'dueDateFlag' in data else None
            # hightest, high, normal, low, lowest, none
            # TODO: hightest is correct?
            self.priority = data['priority'] if 'priority' in data else None
            """
            The priority of the post or the template.
            """

    def __repr__(self):
        ret = f"'users': '{self.users}', 'body': '{self.body}', 'subject': '{self.subject}', " \
              f"'due_date': '{self.due_date}', 'due_date_flag': '{self.due_date_flag}', 'priority': '{self.priority}'"
        return ret


class WritePost(BasePost):
    def __init__(self, data=None):
        super().__init__(data)
        if data is not None:
            self.parent_post_id = data['parentPostId']
            self.version = data['version'] if 'version' in data else None
            self.milestone_id = data['milestoneId']
            self.tag_ids = [tag_id for tag_id in data['tagIds']]

    def __repr__(self):
        return f"{{ {super().__repr__()} " \
               f"'parent_post_id': '{self.parent_post_id}', 'version': '{self.version}', " \
               f"'milestone_id': '{self.milestone_id}', 'tag_ids': '{self.tag_ids}' }}"

    def to_json_dict(self):
        d = {}
        if hasattr(self, 'users') and self.users is not None:
            d['users'] = self.users.to_json_dict()
        if hasattr(self, 'body') and self.body is not None:
            d['body'] = self.body.to_json_dict()
        if hasattr(self, 'subject') and self.subject is not None:
            d['subject'] = self.subject
        if hasattr(self, 'due_date') and self.due_date is not None:
            d['dueDate'] = self.due_date
        if hasattr(self, 'due_date_flag') and self.due_date_flag is not None:
            d['dueDateFlag'] = self.due_date_flag
        if hasattr(self, 'milestone_id') and self.milestone_id is not None:
            d['milestoneId'] = self.milestone_id
        if hasattr(self, 'tag_ids') and self.tag_ids is not None:
            d['tagIds'] = [tag_id for tag_id in self.tag_ids]
        if hasattr(self, 'priority') and self.priority is not None:
            d['priority'] = self.priority
        if hasattr(self, 'version') and self.version is not None:
            d['version'] = self.version
        if hasattr(self, 'parent_post_id') and self.parent_post_id is not None:
            d['parentPostId'] = self.parent_post_id
        return d


class PostBuilder:
    """
    A helper class to write or update a post.

    See :class:`dooray.DoorayProject.create_post` or :class:`dooray.DoorayProject.update_post`.

    Usage::

        import dooray

        d = dooray.Dooray(API_TOKEN)
        post = dooray.PostBuilder()\\
            .set_subject('test')\\
            .set_body('test')\\
            .add_to_member(member_id)\\
            .create()
        d.project.create_post(PROJECT_ID, post)
    """
    def __init__(self):
        self._post = WritePost()

    def create(self):
        """
        Create a new post object to be written.
        """
        return self._post

    def set_parent_post_id(self, parent_post_id):
        """
        Set the parent post id.

        :param parent_post_id: The parent post id.
        :type parent_post_id: str
        """
        self._post.parent_post_id = parent_post_id
        return self

    def set_body(self, body):
        """
        Set the body of the post.

        :param body: The body of the post.
        :type body: str
        """
        self._post.body = PostBody({
            'mimeType': 'text/x-markdown',
            'content': body,
        })
        return self

    def set_subject(self, subject):
        """
        Set the subject of the post.

        :param subject: The subject of the post.
        :type subject: str
        """
        self._post.subject = subject
        return self

    def set_due_date(self, due_date):
        """
        Set the due date of the post.

        :param due_date: The due date of the post in ISO 8601 format.
        :type due_date: str
        """
        self._post.due_date = due_date
        return self

    def set_milestone_id(self, milestone_id):
        """
        Set the milestone id of the post.

        :param milestone_id: The milestone id of the post.
        :type milestone_id: str
        """
        self._post.milestone_id = milestone_id
        return self

    def set_priority(self, priority):
        """
        Set the priority of the post.

        :param priority: The priority of the post. \
            Possible values are: 'highest', 'high', 'normal', 'low', 'lowest' and 'none'
        :type priority: str
        """
        self._post.priority = priority
        return self

    def set_version(self, version):
        """
        Set the version of the post.

        :param version: The version of the post.
        :type version: str
        """
        self._post.version = version
        return self

    def add_tag_id(self, tag_id):
        """
        Add a tag id to the post.

        :param tag_id: The tag id to add.
        :type tag_id: str
        """
        if not hasattr(self._post, 'tag_ids') or self._post.tag_ids is None:
            self._post.tag_ids = []
        self._post.tag_ids.append(tag_id)
        return self

    def add_to_member(self, member_id):
        """
        Add recipient to the post by member ID

        :param member_id: The member ID to add.
        :type member_id: str
        """
        if not hasattr(self._post, 'users') or self._post.users is None:
            self._post.users = PostUsers()
        self._post.users.to.append(PostUser({
            'type': 'member',
            'member': {
                'organizationMemberId': member_id
            }
        }))
        return self

    def add_to_email_user(self, email, name):
        """
        Add recipient to the post by email and name

        :param email: The email of the user to add.
        :type email: str
        :param name: The name of the user to add.
        :type name: str
        """
        if not hasattr(self._post, 'users') or self._post.users is None:
            self._post.users = PostUsers()
        self._post.users.to.append(PostUser({
            'type': 'emailUser',
            'emailUser': {
                'emailAddress': email,
                'name': name
            }
        }))
        return self

    def add_cc_member(self, member_id):
        """
        Add cc recipient to the post by member ID

        :param member_id: The member ID to add.
        :type member_id: str
        """
        if not hasattr(self._post, 'users') or self._post.users is None:
            self._post.users = PostUsers()
        self._post.users.cc.append(PostUser({
            'type': 'member',
            'member': {
                'organizationMemberId': member_id
            }
        }))
        return self

    def add_cc_email_user(self, email, name):
        """
        Add cc recipient to the post by email and name

        :param email: The email of the user to add.
        :type email: str
        :param name: The name of the user to add.
        :type name: str
        """
        if not hasattr(self._post, 'users') or self._post.users is None:
            self._post.users = PostUsers()
        self._post.users.cc.append(PostUser({
            'type': 'emailUser',
            'emailUser': {
                'emailAddress': email,
                'name': name
            }
        }))
        return self


class ReadPost(BasePost):
    def __init__(self, data):
        super().__init__(data)
        self.id = data['id']
        """"""
        self.project = Project(data['project']) if 'project' in data else None
        """
        :type: :class:`dooray.Project.Project`
        """
        self.task_number = data['taskNumber'] if 'taskNumber' in data else None
        """"""
        self.closed = data['closed'] if 'closed' in data else None
        """"""
        self.closed_at = data['closedAt'] if 'closedAt' in data else None
        """"""
        self.updated_at = data['updatedAt'] if 'updatedAt' in data else None
        """"""
        self.number = data['number']
        """"""
        self.parent = ReadPost(data['parent']) if 'parent' in data else None
        """
        :type: :class:`dooray.Project.ReadPost`
        """
        self.workflow_class = data['workflowClass'] if 'workflowClass' in data else None
        """
        The workflow class of the post. Possible values are `registered`, `working` and `closed`
        """
        self.workflow = Workflow(data['workflow']) if 'workflow' in data else None
        """
        :type: :class:`dooray.Project.Workflow`
        """
        # 'milestone' is not returned as null if not set
        self.milestone = Milestone(data['milestone']) if 'milestone' in data and data['milestone'] is not None else None
        """
        :type: :class:`dooray.Project.Milestone`
        """
        self.tags = [Tag(tag) for tag in data['tags']] if 'tags' in data else []
        """
        :type: list of :class:`dooray.Project.Tag`
        """

    def __repr__(self):
        return f"{{ {super().__repr__()}, 'id': '{self.id}', 'project': '{self.project}' " \
               f"'task_number': '{self.task_number}', 'closed': '{self.closed}', " \
               f"'closed_at': '{self.closed_at}', 'updated_at': '{self.updated_at}', " \
               f"'number': '{self.number}', 'parent': '{self.parent}', " \
               f"'workflow_class': '{self.workflow_class}', 'workflow': '{self.workflow}'" \
               f"'milestone': '{self.milestone}', 'tags': '{self.tags}' }}"


class WriteTemplate(BasePost):
    def __init__(self, data=None):
        super().__init__(data)
        if data is not None:
            self.template_name = data['templateName']
            self.guide = PostBody(data['guide'])
            self.is_default = data['isDefault']
            self.milestone_id = data['milestoneId']
            self.tag_ids = [tag_id for tag_id in data['tagIds']]

    def __repr__(self):
        return f"{{ {super().__repr__()} " \
               f"'template_name': '{self.template_name}', 'guide': '{self.guide}', " \
               f"'is_default': '{self.is_default}', 'milestone_id': '{self.milestone_id}', " \
               f"'tag_ids': '{self.tag_ids}' }}"

    def to_json_dict(self):
        # Only 'templateName' is essential, the others are optional
        d = {'templateName': self.template_name}
        if hasattr(self, 'users') and self.users is not None:
            d['users'] = self.users.to_json_dict()
        if hasattr(self, 'body') and self.body is not None:
            d['body'] = self.body.to_json_dict()
        if hasattr(self, 'guide') and self.guide is not None:
            d['guide'] = self.guide.to_json_dict()
        if hasattr(self, 'subject') and self.subject is not None:
            d['subject'] = self.subject
        if hasattr(self, 'due_date') and self.due_date is not None:
            d['dueDate'] = self.due_date
        if hasattr(self, 'due_date_flag') and self.due_date_flag is not None:
            d['dueDateFlag'] = self.due_date_flag
        if hasattr(self, 'milestone_id') and self.milestone_id is not None:
            d['milestoneId'] = self.milestone_id
        if hasattr(self, 'tag_ids') and self.tag_ids is not None:
            d['tagIds'] = [tag_id for tag_id in self.tag_ids]
        if hasattr(self, 'priority') and self.priority is not None:
            d['priority'] = self.priority
        if hasattr(self, 'is_default') and self.is_default is not None:
            d['isDefault'] = self.is_default
        return d


class TemplateBuilder:
    """
    A helper class to write or update a post template.

    See :class:`dooray.DoorayProject.create_template` or :class:`dooray.DoorayProject.update_template`.

    Usage::

        import dooray

        d = dooray.Dooray(API_TOKEN)
        post = dooray.TemplateBuilder()\\
            .set_subject('test')\\
            .set_body('test')\\
            .add_to_member(member_id)\\
            .create()
        d.project.create_template(PROJECT_ID, post)
    """
    def __init__(self):
        self._template = WriteTemplate()

    def create(self):
        """
        Create a new post object to be written.
        """
        return self._template

    def set_template_name(self, template_name):
        """
        Set the template name.

        :param template_name: The template name.
        :type template_name: str
        """
        self._template.template_name = template_name
        return self

    def set_body(self, body):
        """
        Set the body of the template.

        :param body: The body of the template.
        :type body: str
        """
        self._template.body = PostBody({
            'mimeType': 'text/x-markdown',
            'content': body,
        })
        return self

    def set_guide(self, guide):
        """
        Set the guide of the template.

        :param guide: The guide of the template.
        :type guide: str
        """
        self._template.guide = PostBody({
            'mimeType': 'text/x-markdown',
            'content': guide,
        })
        return self

    def set_subject(self, subject):
        """
        Set the subject of the template.

        :param subject: The subject of the template.
        :type subject: str
        """
        self._template.subject = subject
        return self

    def set_due_date(self, due_date):
        """
        Set the due date of the template.

        :param due_date: The due date of the template in ISO 8601 format.
        :type due_date: str
        """
        self._template.due_date = due_date
        return self

    def set_milestone_id(self, milestone_id):
        """
        Set the milestone id of the template.

        :param milestone_id: The milestone id of the template.
        :type milestone_id: int
        """
        self._template.milestone_id = milestone_id
        return self

    def set_priority(self, priority):
        """
        Set the priority of the template.

        :param priority: The priority of the template. \
            Possible values are: 'highest', 'high', 'normal', 'low', 'lowest' and 'none'
        :type priority: str
        """
        self._template.priority = priority
        return self

    def set_is_default(self, is_default):
        """
        Set if this template is the default template of this project or not.

        :param is_default: If true, this template is the default template of this project.
        :type is_default: bool
        """
        self._template.is_default = is_default
        return self

    def add_tag_id(self, tag_id):
        """
        Add a tag id to the post.

        :param tag_id: The tag id to add.
        :type tag_id: str
        """
        if not hasattr(self._template, 'tag_ids') or self._template.tag_ids is None:
            self._template.tag_ids = []
        self._template.tag_ids.append(tag_id)
        return self

    def add_to_member(self, member_id):
        """
        Add recipient to the template by member ID

        :param member_id: The member ID to add.
        :type member_id: str
        """
        if not hasattr(self._template, 'users') or self._template.users is None:
            self._template.users = PostUsers()
        self._template.users.to.append(PostUser({
            'type': 'member',
            'member': {
                'organizationMemberId': member_id
            }
        }))
        return self

    def add_to_email_user(self, email, name):
        """
        Add recipient to the template by email and name

        :param email: The email of the user to add.
        :type email: str
        :param name: The name of the user to add.
        :type name: str
        """
        if not hasattr(self._template, 'users') or self._template.users is None:
            self._template.users = PostUsers()
        self._template.users.to.append(PostUser({
            'type': 'emailUser',
            'emailUser': {
                'emailAddress': email,
                'name': name
            }
        }))
        return self

    def add_cc_member(self, member_id):
        """
        Add cc recipient to the template by member ID

        :param member_id: The member ID to add.
        :type member_id: str
        """
        if not hasattr(self._template, 'users') or self._template.users is None:
            self._template.users = PostUsers()
        self._template.users.cc.append(PostUser({
            'type': 'member',
            'member': {
                'organizationMemberId': member_id
            }
        }))
        return self

    def add_cc_email_user(self, email, name):
        """
        Add cc recipient to the template by email and name

        :param email: The email of the user to add.
        :type email: str
        :param name: The name of the user to add.
        :type name: str
        """
        if not hasattr(self._template, 'users') or self._template.users is None:
            self._template.users = PostUsers()
        self._template.users.cc.append(PostUser({
            'type': 'emailUser',
            'emailUser': {
                'emailAddress': email,
                'name': name
            }
        }))
        return self


class ReadTemplate(BasePost):
    def __init__(self, data):
        super().__init__(data)
        self.id = data['id']
        """"""
        self.project = Project(data['project'])
        """
        :type: :class:`dooray.Project.Project`
        """
        self.template_name = data['templateName']
        """"""
        self.guide = PostBody(data['guide']) if 'guide' in data else None
        """
        :type: :class:`dooray.Project.PostBody`
        """
        self.is_default = data['isDefault']
        """
        :type: bool
        """
        # 'milestone' is not returned if no milestones set
        self.milestone = Milestone(data['milestone']) if 'milestone' in data else None
        """
        :type: :class:`dooray.Project.Milestone`
        """
        self.tags = [Tag(tag) for tag in data['tags']]
        """
        :type: list of :class:`dooray.Project.Tag`
        """

    def __repr__(self):
        return f"{{ {super().__repr__()}, 'id': '{self.id}', 'project': '{self.project}' " \
               f"'template_name': '{self.template_name}', 'guide': '{self.guide}', " \
               f"'is_default': '{self.is_default}', 'milestone': '{self.milestone}', " \
               f"'tags': '{self.tags}' }}"


class PostLog:
    def __init__(self, data):
        self.id = data['id']
        """"""
        self.post = dooray.DoorayObjects.Relation(data['post'])
        """
        :type: :class:`dooray.DoorayObjects.Relation`
        """
        self.type = data['type']
        """
        The type of log. Possible values are `comment` and 'event`.
        """
        self.subtype = data['subtype']
        """
        the subtype of the log. Possible values are `general`, `from_email` and `sent_email`.
        """
        self.created_at = data['createdAt']
        """"""
        self.modified_at = data['modifiedAt'] if 'modifiedAt' in data else None
        """"""
        self.creator = PostUser(data['creator'])
        """
        :type: :class:`dooray.Project.PostUser`
        """
        self.mailUsers = PostUsers(data['mailUsers']) if 'mailUsers' in data else None
        """
        :type: :class:`dooray.Project.PostUsers`
        """
        self.body = PostBody(data['body'])
        """
        :type: :class:`dooray.Project.PostBody`
        """

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'post': {self.post}, 'type': '{self.type}', " \
               f"'subtype': '{self.subtype}', 'created_at': '{self.created_at}', " \
               f"'modified_at': '{self.modified_at}', 'creator': {self.creator}, " \
               f"'mailUsers': {self.mailUsers}, 'body': {self.body} }}"


class PostUser:
    def __init__(self, data):
        self.type = data['type']
        """"""
        self.member = ProjectMember(data['member']) if 'member' in data else None
        """
        :type: :class:`dooray.Project.ProjectMember`
        """
        self.email_user = EmailAddress(data['emailUser']) if 'emailUser' in data else None
        """
        :type: :class:`dooray.Project.EmailAddress`
        """

    def __repr__(self):
        return f"{{ 'type': '{self.type}', 'member': {self.member}, 'email_user': {self.email_user} }}"

    def to_json_dict(self):
        d = {'type': self.type}
        if self.type == 'member':
            d['member'] = self.member.to_json_dict()
        elif self.type == 'emailUser':
            d['emailUser'] = self.email_user.to_json_dict()
        return d


class PostUsers:
    def __init__(self, data=None):
        if data is not None:
            self.user_from = PostUser(data['from']) if 'from' in data else None
            """
            :type: :class:`dooray.Project.PostUser`
            """
            self.to = [PostUser(u) for u in data['to']]
            """
            :type: list of :class:`dooray.Project.PostUser`
            """
            self.cc = [PostUser(u) for u in data['cc']]
            """
            :type: list of :class:`dooray.Project.PostUser`
            """
        else:
            self.user_from = None
            self.to = []
            self.cc = []

    def __repr__(self):
        return f"{{ 'user_from': {self.user_from}, 'to': {self.to}, 'cc': {self.cc} }}"

    def to_json_dict(self):
        return {
            'from': self.user_from,
            'to': [u.to_json_dict() for u in self.to],
            'cc': [u.to_json_dict() for u in self.cc],
        }


class PostBody:
    def __init__(self, data):
        self.mime_type = data['mimeType']
        """"""
        self.content = data['content']
        """"""

    def __repr__(self):
        return f"{{ 'mime_type': '{self.mime_type}', 'content': '{self.content}' }}"

    def to_json_dict(self):
        return {
            'mimeType': self.mime_type,
            'content': self.content,
        }
