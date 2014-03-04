# Mycroft Python

App template for python

## Installation
Got to the directory and run the following command:
```
python setup.py install
```

## Running your app
```
python YOUR_APP.py [--no-tls]
```

## Example App
```python
from mycroft.client import MycroftClient

def app_dependency(client, msg_type, data):
    client.update_dependencies(data)
    client.up()
    client.query('stt','testing',{})
    client.broadcast({})


client = MycroftClient('localhost', 1847, './app.json')
client.on('APP_DEPENDENCY', app_dependency)
client.start()
```

### Overview
The python app template is event driven. Create handlers for the types of messages you would like to respond to and add them to the client using the `on` method. As well as all the messages, you can also create handlers for `'connect'` and `'end'`. Any extra initialization should be done in the `connect` handler. Or you can subclass. Whatever floats your boat.

### Helper Methods

#### up()
Sends `APP_UP` to mycroft

#### down()
Sends `APP_DOWN` to mycroft

#### in_use(priority=30)
Sends `APP_IN_USE` to mycroft

#### query(capability, action, data, instance_id = None, priority = 30)
Sends a `MSG_QUERY` to mycroft

#### broadcast(content)
Sends a `MSG_BROADCAST` to mycroft

#### query_success(id, ret)
Sends a `MSG_QUERY_SUCCESS` to mycroft

#### query_fail(id, message)
Sends a `MSG_QUERY_FAIL` to mycroft

#### update_dependencies(dependencies)
Takes the dependency json object and updates `self.dependencies` accordingly. 
