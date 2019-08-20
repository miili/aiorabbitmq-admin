import unittest
import os
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import pika
import aiohttp

from aiorabbitmq_admin.api import AdminAPI

USERNAME = 'guest'
PASSWORD = 'guest'


class AdminAPITests(AioHTTPTestCase):
    """
    These test cases require a docker container up and running
    ::

        docker run -d \
            -h rabbit1 \
            -p 5672:5672 \
            -p 15672:15672 \
            -e RABBITMQ_DEFAULT_USER=guest \
            -e RABBITMQ_DEFAULT_PASS=guest \
            -name rabbit1 \
            rabbitmq:3-management

    """

    @classmethod
    def setUpClass(cls):
        """
        One-time set up that connects as USERNAME, creates a 'test_queue' and
        sends one message

        TravisCI sometimes turns on RabbitMQ when we don't want it, so we use
        alternative ports 5673 and 15673
        """
        if os.environ.get('TRAVIS'):  # pragma: no cover
            cls.host = '127.0.0.1'
            cls.amqp_port = 5673
            cls.admin_port = 15673
        else:  # pragma: no cover
            cls.host = os.environ.get('RABBITMQ_HOST', '192.168.99.100')
            cls.amqp_port = 5672
            cls.admin_port = 15672

        credentials = pika.PlainCredentials(USERNAME, PASSWORD)
        cls.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                cls.host,
                port=cls.amqp_port,
                credentials=credentials
            ),
        )
        channel = cls.connection.channel()
        channel.queue_declare(queue='test_queue')
        channel.basic_publish(
            exchange='',
            routing_key='test_queue',
            body='Test Message')

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    async def get_application(self):

        async def hello(request):
            return aiohttp.web.Response(text='Hello, world')

        app = aiohttp.web.Application()
        app.router.add_get('/', hello)
        return app

    async def setUpAsync(self):
        url = 'http://{host}:{port}'.format(host=self.host, port=self.admin_port)

        self.api = AdminAPI(url, auth=(USERNAME, PASSWORD))
        self.node_name = 'rabbit@rabbit1'

    async def tearDownAsync(self):
        try:
            await self.api.delete_user('user2')
        except aiohttp.client_exceptions.ClientResponseError:
            pass

        try:
            await self.api.delete_user('test_user')
        except aiohttp.client_exceptions.ClientResponseError:
            pass

        try:
            await self.api.delete_exchange_for_vhost('myexchange', '/')
        except aiohttp.client_exceptions.ClientResponseError:
            pass

    @unittest_run_loop
    async def test_overview(self):
        response = await self.api.overview()
        self.assertIsInstance(response, dict)

    @unittest_run_loop
    async def test_get_cluster_name(self):
        await self.api.get_cluster_name(),

    @unittest_run_loop
    async def test_list_nodes(self):
        self.assertEqual(
            len(await self.api.list_nodes()),
            1
        )

    @unittest_run_loop
    @unittest.skip
    async def test_get_node(self):
        resp = await self.api.get_cluster_name()
        node_name = resp['name'].split('@')[0]

        response = await self.api.get_node(node_name)
        self.assertIsInstance(response, dict)
        self.assertEqual(response['name'], node_name)

    @unittest_run_loop
    async def test_list_extensions(self):
        self.assertEqual(
            await self.api.list_extensions(),
            [{'javascript': 'dispatcher.js'}]
        )

    @unittest_run_loop
    async def test_get_definitions(self):
        response = await self.api.get_definitions()
        self.assertEqual(len(response['users']), 1)
        self.assertEqual(len(response['vhosts']), 1)

    @unittest_run_loop
    async def test_post_definitions(self):
        response = await self.api.get_definitions()
        await self.api.post_definitions(response)

    @unittest_run_loop
    async def test_list_connections(self):
        await self.api.list_connections()

    @unittest_run_loop
    async def test_get_connection(self):
        resp = await self.api.list_connections()
        cname = resp[0].get('name')
        self.assertIsInstance(
            await self.api.get_connection(cname),
            dict
        )

    @unittest_run_loop
    async def test_delete_connection(self):
        with self.assertRaises(aiohttp.client_exceptions.ClientResponseError):
            await self.api.delete_connection('not-a-connection')

    @unittest_run_loop
    async def test_delete_connection_with_reason(self):
        with self.assertRaises(aiohttp.client_exceptions.ClientResponseError):
            await self.api.delete_connection('not-a-connection', 'I don\'t like you')

    @unittest_run_loop
    async def test_list_connection_channels(self):
        resp = await self.api.list_connections()
        cname = resp[0].get('name')

        response = await self.api.list_connection_channels(cname)

        self.assertEqual(
            response[0].get('name'),
            cname + ' (1)'
        )

    @unittest_run_loop
    async def test_list_channels(self):
        await self.api.list_channels()

    @unittest_run_loop
    async def test_get_channel(self):
        resp = await self.api.list_channels()
        cname = resp[0].get('name')

        self.assertIsInstance(
            await self.api.get_channel(cname),
            dict
        )

    @unittest_run_loop
    async def test_list_consumers(self):
        await self.api.list_consumers()

    @unittest_run_loop
    async def test_list_consumers_for_vhost(self):
        await self.api.list_consumers_for_vhost('/')

    @unittest_run_loop
    async def test_list_exchanges(self):
        await self.api.list_exchanges()

    @unittest_run_loop
    async def test_list_exchanges_for_vhost(self):
        await self.api.list_exchanges_for_vhost('/')

    @unittest_run_loop
    async def test_get_create_delete_exchange_for_vhost(self):
        name = 'myexchange'
        body = {
            "type": "direct",
            "auto_delete": False,
            "durable": False,
            "internal": False,
            "arguments": {}
        }
        nexchanges = len(await self.api.list_exchanges_for_vhost('/'))

        await self.api.create_exchange_for_vhost(name, '/', body)
        self.assertEqual(
            len(await self.api.list_exchanges_for_vhost('/')),
            nexchanges + 1
        )
        resp = await self.api.get_exchange_for_vhost(name, '/')
        self.assertEqual(
            resp.get('name'),
            name
        )

        await self.api.delete_exchange_for_vhost(name, '/')
        self.assertEqual(
            len(await self.api.list_exchanges_for_vhost('/')),
            nexchanges
        )

    @unittest_run_loop
    async def test_list_bindings(self):
        await self.api.list_bindings()

    @unittest_run_loop
    async def test_list_bindings_for_vhost(self):
        await self.api.list_bindings_for_vhost('/')

    @unittest_run_loop
    async def test_list_vhosts(self):
        response = await self.api.list_vhosts()
        self.assertEqual(
            len(response),
            1
        )
        self.assertEqual(response[0].get('name'), '/')

    @unittest_run_loop
    async def test_get_vhosts(self):
        response = await self.api.get_vhost('/')
        self.assertEqual(response.get('name'), '/')

    @unittest_run_loop
    async def test_create_delete_vhost(self):
        name = 'vhost2'

        await self.api.create_vhost(name)
        self.assertEqual(
            len(await self.api.list_vhosts()),
            2
        )

        await self.api.delete_vhost(name)
        self.assertEqual(
            len(await self.api.list_vhosts()),
            1
        )

    @unittest_run_loop
    async def test_create_delete_vhost_tracing(self):
        name = 'vhost2'

        await self.api.create_vhost(name, tracing=True)
        self.assertEqual(
            len(await self.api.list_vhosts()),
            2
        )

        await self.api.delete_vhost(name)
        self.assertEqual(
            len(await self.api.list_vhosts()),
            1
        )

    @unittest_run_loop
    async def test_list_users(self):
        self.assertEqual(
            len(await self.api.list_users()),
            1
        )

    @unittest_run_loop
    async def test_get_user(self):
        response = await self.api.get_user(USERNAME)
        self.assertEqual(response.get('name'), USERNAME)
        self.assertEqual(response.get('tags'), 'administrator')

    @unittest_run_loop
    async def test_create_delete_user(self):
        name = 'user2'
        password_hash = '5f4dcc3b5aa765d61d8327deb882cf99'  # md5 of 'password'

        await self.api.create_user(
            name, password='', password_hash=password_hash)
        self.assertEqual(
            len(await self.api.list_users()),
            2
        )

        await self.api.delete_user(name)
        self.assertEqual(
            len(await self.api.list_users()),
            1
        )

    @unittest_run_loop
    async def test_create_delete_user_password(self):
        name = 'user2'
        password = 'password'
        nusers = len(await self.api.list_users())

        await self.api.create_user(name, password=password)
        self.assertEqual(
            len(await self.api.list_users()),
            nusers + 1
        )

        await self.api.delete_user(name)
        self.assertEqual(
            len(await self.api.list_users()),
            nusers
        )

    @unittest_run_loop
    async def test_create_delete_user_no_password(self):
        name = 'user2'
        password = ''
        nusers = len(await self.api.list_users())

        await self.api.create_user(name, password=password)
        self.assertEqual(
            len(await self.api.list_users()),
            nusers + 1
        )

        await self.api.delete_user(name)
        self.assertEqual(
            len(await self.api.list_users()),
            nusers
        )

    @unittest_run_loop
    async def test_list_user_permissions(self):
        self.assertEqual(
            await self.api.list_user_permissions(USERNAME),
            [{'configure': '.*',
              'read': '.*',
              'user': USERNAME,
              'vhost': '/',
              'write': '.*'}]
        )

    @unittest_run_loop
    async def test_whoami(self):
        self.assertEqual(
            await self.api.whoami(),
            {'name': USERNAME, 'tags': 'administrator'}
        )

    @unittest_run_loop
    async def test_list_permissions(self):
        self.assertEqual(
            await self.api.list_permissions(),
            [{'configure': '.*',
              'read': '.*',
              'user': USERNAME,
              'vhost': '/',
              'write': '.*'}]
        )

    @unittest_run_loop
    async def test_get_user_permission(self):
        self.assertEqual(
            await self.api.get_user_permission('/', USERNAME),
            {
                'configure': '.*',
                'read': '.*',
                'user': USERNAME,
                'vhost': '/',
                'write': '.*'
            }
        )

    @unittest_run_loop
    async def test_create_delete_user_permission(self):
        uname = 'test_user'
        vname = 'test_vhost'
        password_hash = '5f4dcc3b5aa765d61d8327deb882cf99'  # md5 of 'password'


        # Create test user/vhost
        await self.api.create_user(uname, password='', password_hash=password_hash)
        await self.api.create_vhost(vname)
        npermissions = len(await self.api.list_user_permissions(uname))

        self.assertEqual(
            len(await self.api.list_user_permissions(uname)),
            npermissions)

        # Create the permission
        await self.api.create_user_permission(uname, vname)

        self.assertEqual(
            len(await self.api.list_user_permissions(uname)),
            npermissions + 1)

        # Delete the permission
        await self.api.delete_user_permission(uname, vname)

        self.assertEqual(
            len(await self.api.list_user_permissions(uname)),
            npermissions)
        # delete test user/vhost
        await self.api.delete_user(uname)
        await self.api.delete_vhost(vname)

    @unittest_run_loop
    async def test_policies(self):
        # Create a policy
        await self.api.create_policy_for_vhost(
            vhost="/",
            name="ha-all",
            definition={"ha-mode": "all"},
            pattern="",
            apply_to="all",
        )

        list_all_response = await self.api.list_policies()
        list_default_response = await self.api.list_policies_for_vhost("/")

        self.assertEqual(list_all_response, list_default_response)
        self.assertEqual(len(list_default_response), 1)

        with self.assertRaises(aiohttp.client_exceptions.ClientResponseError):
            await self.api.get_policy_for_vhost("/", "not-a-policy")

        get_response = await self.api.get_policy_for_vhost("/", "ha-all")
        self.assertEqual(
            get_response,
            list_all_response[0]
        )

        await self.api.delete_policy_for_vhost("/", "ha-all")
        self.assertEqual(
            len(await self.api.list_policies()),
            0
        )

    @unittest_run_loop
    async def test_is_vhost_alive(self):
        self.assertDictEqual(
            await self.api.is_vhost_alive('/'),
            {'status': 'ok'}
        )
