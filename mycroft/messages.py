import uuid
import json
import socket


class MessagesMixin:

    def send_manifest(self, manifest):
        """
        Send the manifest to Mycroft
        Args:
            manifest - str or file-like object
        """
        if not hasattr(manifest, 'read'):
            manifest = open(self.manifest)
        message = manifest.read()
        manifest.close()
        message = json.loads(message)
        if hasattr(self, 'generate_instace_ids'):
            if self.generate_instance_ids:
                message['instanceId'] = "{0}_{1}".format(socket.gethostname(), str(uuid.uuid4()))
        self.send_message('APP_MANIFEST', message)

    def up(self):
        """
        Send APP_UP to Mycroft
        """
        self.send_message('APP_UP')

    def down(self):
        """
        Send APP_DOWN to Mycroft
        """
        self.send_message('APP_DOWN')

    def in_use(self, priority=30):
        """
        Send APP_IN_USE to Mycroft
        Args:
            priority - optional, int indicating priority
                       (default 30)
        """
        self.send_message('APP_IN_USE', {'priority': priority})

    def query(self, capability, action, data, instance_id=[], priority=30):
        """
        Send MSG_QUERY to Mycroft
        Args:
            capability - str, the target capability
            action - str, the action on the target app
            data - JSON serializable, usually dict, data to send in body
            instance_id - optional, array of target instances to query
                          (default all)
            priority - optional, int default 30
        """
        query_message = {
            'id': str(uuid.uuid4()),
            'capability': capability,
            'action': action,
            'data': data,
            'priority': priority,
            'instanceId': instance_id
        }

        self.send_message('MSG_QUERY', query_message)

    def query_success(self, message_id, ret):
        """
        Send MSG_QUERY_SUCCESS to Mycroft
        Args:
            message_id - the ID of the message to which you are repsonding
            ret - returned data
        """
        query_success_message = {
            'id': message_id,
            'ret': ret
        }

        self.send_message('MSG_QUERY_SUCCESS', query_success_message)

    def query_fail(self, message_id, message):
        """
        Send MSG_QUERY_FAIL to Mycroft
        Args:
            message_id - the ID of the message to which you are responding
            message - str, why the query failed generally
        """
        query_fail_message = {
            'id': message_id,
            'message': message
        }

        self.send_message('MSG_QUERY_FAIL', query_fail_message)

    def broadcast(self, content):
        """
        Send a MSG_BROADCAST to Mycroft
        Args:
            content - dict, what you are sending out
        """
        message = {
            'id': str(uuid.uuid4()),
            'content': content
        }

        self.send_message('MSG_BROADCAST', message)
