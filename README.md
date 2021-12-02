# PyDooray

PyDooray is a Python library to access the [Dooray! REST API].
This library enables you to access [Dooray!] services such as messenger, project, calendar, drive and wiki in your Python applications.

[Dooray! REST API]: https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2937064454837487755
[Dooray!]: https://dooray.com/

## How to use

### Messenger Hook
```python
import dooray

MESSENGER_HOOK_URL = '<Your hook url>'
MESSENGER_HOOK_ICON_URL = '<Your hook icon url>'

hook = dooray.MessengerHook(MESSENGER_HOOK_URL, hook_name="My Bot", hook_icon=MESSENGER_HOOK_ICON_URL)
hook.send('Send text only')

attachments = [
    {
        "title": "title only",
    },
    {
        "title": "title with link",
        "titleLink": "http://dooray.com/",
        "text": "green message box",
        "color": "green"
    },
]
hook.send('Send Text with attachments', attachments=attachments)

attachments = dooray.MessengerHookAttachments.builder()\
    .add_attachment(title='title by builder', title_link= 'http://dooray.com/', text='text by builder', color='yellow')\
    .add_attachment(text='text in purple box', color='purple')\
    .create()
hook.send('Send Text with attachments builder', attachments=attachments)
```

### Messenger
```python
import dooray

DOORAY_API_TOKEN = '<Your Dooray! API Token>'

CHANNEL_TITLE = '<Channel Title>'
MEMBER_TO_INVITE = '<Email address of a member>'

d = dooray.Dooray(DOORAY_API_TOKEN)

member = d.get_members(external_emails=MEMBER_TO_INVITE)
member_id_list = [ member.result[0].id ]

channel = d.messenger.create_channel(CHANNEL_TITLE, member_id_list)
channel_id = channel.result.id

d.messenger.send_channel_message(channel_id, 'Send Message to Channel')

d.messenger.leave_channel(channel_id, member_id_list)

d.messenger.join_channel(channel_id, member_id_list)
```