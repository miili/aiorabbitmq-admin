[![Build Status](https://travis-ci.org/miili/aiorabbitmq-admin.svg?branch=master)](https://travis-ci.org/miili/aiorabbitmq-admin)

aiorabbitmq-admin
=================
An asynchronous python wrapper around the RabbitMQ Management HTTP API based on [aiohttp](https://docs.aiohttp.org).
This project is forked from [rabbitmq-admin](https://github.com/ambitioninc/rabbitmq-admin). Thanks to Micah Hausler!


Example
-------

```python
>>> import asyncio
>>> from rabbitmq_admin import AdminAPI
>>> api = AdminAPI(url='http://192.168.99.100:15672', auth=('guest', 'guest'))
>>>
>>> async def my_commands():
>>>   api.create_vhost('second_vhost')
>>>   api.create_user('second_user', 'password')
>>>   api.create_user_permission('second_user', 'second_vhost')
>>>   print(api.list_permission())
>>>
>>> loop = asyncio.get_event_loop()
>>> loop.run_until_complete(my_commands())
[{'configure': '.*',
  'read': '.*',
  'user': 'guest',
  'vhost': '/',
  'write': '.*'},
 {'configure': '.*',
  'read': '.*',
  'user': 'second_user',
  'vhost': 'second_vhost',
  'write': '.*'}]
```

Unsupported Management API endpoints
------------------------------------
This is a list of unsupported API endpoints. Please do not make issues for
these, but pull requests implementing them are welcome.

- ``/api/exchanges/vhost/name/bindings/source [GET]``
- ``/api/exchanges/vhost/name/bindings/destination [GET]``
- ``/api/exchanges/vhost/name/publish [POST]``
- ``/api/queues/vhost/name/bindings [GET]``
- ``/api/queues/vhost/name/contents [DELETE]``
- ``/api/queues/vhost/name/actions [POST]``
- ``/api/queues/vhost/name/get [POST]``
- ``/api/bindings/vhost/e/exchange/q/queue [GET, POST]``
- ``/api/bindings/vhost/e/exchange/q/queue/props [GET, DELETE]``
- ``/api/bindings/vhost/e/source/e/destination [GET, POST]``
- ``/api/bindings/vhost/e/source/e/destination/props [GET, DELETE]``
- ``/api/parameters [GET]``
- ``/api/parameters/component [GET]``
- ``/api/parameters/component/vhost [GET]``
- ``/api/parameters/component/vhost/name [GET, PUT, DELETE]``

Installation
------------

To install the latest code directly from source, type:

```bash
pip3 install git+https://github.com/miili/aiorabbitmq-admin.git
```

Documentation
-------------
This project is forked from `rabbitmq-admin`. Full documentation is available at http://rabbitmq-admin.readthedocs.org

License
-------
MIT License (see LICENSE)
