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