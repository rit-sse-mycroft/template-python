# Mycroft Python

App template for python

## Installation
Got to the directory and run the following command:
```
python setup.py install
```

## Starting a new app

```
python -m mycroft init
```

This will prompt you for details about your new app and generate a manifest and main module.

## Running your app
```
python YOUR_APP.py [--no-tls]
```

## Example App
```python
import mycroft

class MyApp(mycroft.App):

    @mycroft.on('APP_MANIFEST_OK')
    def manifest_verified(self, event_name, body):
        self.up()

app = MyApp()
app.start(
    './manifest.json',
    'my app'
)
```

## Overview
Python apps extend the base class `Mycroft.App`. Interactions with Mycroft are event driven. Register methods
of your class by using the `@mycroft.on('event_name')` decorator. When the application is started these
events are fired accordingly. Your application also contains helper methods (from the superclass `mycroft.App`)
which are listed below. The application is started via `App.start()`. Your dependencies are stored in the
`self.dependencies` variable as a dictionary which maps from capabilities to a dictionary of instance IDs to a string representing the instance's status.

### Events

Events are registered through the `@mycroft.on('event_name')` decorator. There are two types of events
that can be triggered, internal and external events. The former are fired for events which are
internal to the application. The latter are fired in response to Mycroft messages, and their event name
is the verb which Mycroft sends, for example `'MSG_QUERY'`.

#### Internal events

The Mycroft package offers the following internal event triggers:

* `before_connect` - fired immediately all handlers are registered and before attempting to connect to Mycroft
* `after_connect` - fired after a connection to Mycroft is attained
* `before_send_manifest` - fired before the Manifest is sent
* `after_send_manifest` - fired after the Manifest is sent
* `before_event_loop` - fired before the event loop (listening for messages) is entered
* `before_read` - fired before waiting for a message
* `after_read` - fired after a message was processed
* `before_handle_close` - fired before the app sends APP_DOWN and disconnects from mycroft
* `after_handle_close` - fired after the app sends APP_DOWN and disconnects from mycroft
* `end` - fired after the application has closed, forcibly or otherwise (NOTE: this will not get fired the application has not been able to parse handlers yet)

An event handler for internal events should only accept one argument, the name of the event being fired. For example:

```python
@mycroft.on('before_connect')
def foo(self, ev_name):
    pass
```

#### External events

These events are fired as Mycroft communicates with the app. External events should accept two arguments, the name of the event (the verb) and the parsed json data (the body). For example:

```python
@mycroft.on('MSG_QUERY')
def foo(self, ev_name, body):
    pass
```

### The `.start()` method

The `app.start()` method will launch your app, connect to Mycroft, send the manifest, and start processing events. It takes the following arguments:

* `manifest` - required, either a string representing the path to the manifest or a file-like readable object
* `name` - the name of the application, string
* `host` - optional, str, the host to which the application connects (default `'localhost'`)
* `port` - optional, int, the port to which the application connects (default `1847`)
* `key_path` - optional, str, the path to the application's keyfile
* `cert_path` - optional, str, the path to the application's certificate
* `silent` - optional, bool, when True the application will produce no logging messages (default False)


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

#### on(event_name, func)
Register the function to be called when the given event is triggered
