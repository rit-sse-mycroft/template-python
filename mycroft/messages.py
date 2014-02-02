import uuid
class MessagesMixin:
    # Sends App Manifest to mycroft
    def send_manifest(self):
        f = open(self.manifest)
        message = json.loads(f.read())
        self.send_message('APP_MANIFEST', message)

    # Checks if manifest is valid
    def check_manifest(self, parsed):
        if parsed['type'] == 'APP_MANIFEST_OK':
            print('Manifest Validated')
        elif(parsed['type'] == 'APP_MANIFEST_FAIL'):
            raise Exception("Invalid Application Manifest")

    # Sends app up to mycroft
    def up(self):
        self.send_message('APP_UP')

    # Sends app down to mycroft
    def down(self):
        self.send_message('APP_DOWN')

    # Sends app in use to mycroft
    def in_use(self, priority=30):
        self.send_message('APP_IN_USE', {'priority': priority})

    # Sends a query to mycroft
    def query(self, capability, action, data, instance_id=[], priority=30):
        query_message = {
            'id': str(uuid.uuid4()),
            'capability': capability,
            'action': action,
            'data': data,
            'priority': priority,
            'instanceId': instance_id
        }

        self.send_message('MSG_QUERY', query_message)

    # Sends query success to mycroft
    def query_success(self, message_id, ret):
        query_success_message = {
            'id': message_id,
            'ret': ret
        }

        self.send_message('MSG_QUERY_SUCCESS', query_success_message)

    # Sends query fail to mycroft
    def query_fail(self, message_id, message):
        query_fail_message = {
            'id': message_id,
            'message': message
        }

        self.send_message('MSG_QUERY_FAIL', query_fail_message)

    # Send broadcast to mycroft
    def broadcast(self, content):
        message = {
            'id': str(uuid.uuid4()),
            'content': content
        }

        self.send_message('MSG_BROADCAST', message)
