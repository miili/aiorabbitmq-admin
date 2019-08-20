import json
import aiohttp
from copy import deepcopy


class Resource(object):
    """
    A base class for API resources
    """

    # """List of allowed methods, allowed values are
    # ```['GET', 'PUT', 'POST', 'DELETE']``"""
    # ALLOWED_METHODS = []

    def __init__(self, url, auth):
        """
        :param url: The RabbitMQ API url to connect to. This should include the
            protocol and port number.
        :type url: str

        :param auth: The authentication to pass to the request. See
            `aiohttp' authentication`_ documentation. For the simplest case of
            a username and password, simply pass in a tuple of
            ``('username', 'password')``
        :type auth: Requests auth

        .. _Requests' authentication: https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.BasicAuth
        """
        self.url = url.rstrip('/')
        if isinstance(auth, tuple):
            auth = aiohttp.BasicAuth(*auth)
        self.auth = auth

        self.headers = {
            'Content-type': 'application/json',
        }

        self.session_args = {
            'raise_for_status': True
        }

    async def _api_get(self, url, **kwargs):
        """
        A convenience wrapper for _get. Adds headers, auth and base url by
        default
        """
        kwargs['url'] = self.url + url
        kwargs['auth'] = self.auth

        headers = deepcopy(self.headers)
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        return await self._get(**kwargs)

    async def _get(self, *args, **kwargs):
        """
        A wrapper for getting things

        :returns: The response of your get
        :rtype: dict
        """
        async with aiohttp.ClientSession(**self.session_args) as session:
            async with session.get(*args, **kwargs) as resp:
                return await resp.json()

    async def _api_put(self, url, **kwargs):
        """
        A convenience wrapper for _put. Adds headers, auth and base url by
        default
        """
        kwargs['url'] = self.url + url
        kwargs['auth'] = self.auth

        headers = deepcopy(self.headers)
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers
        await self._put(**kwargs)

    async def _put(self, *args, **kwargs):
        """
        A wrapper for putting things. It will also json encode your 'data' parameter

        :returns: The response of your put
        :rtype: dict
        """
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data']).encode()

        async with aiohttp.ClientSession(**self.session_args) as session:
            await session.put(*args, **kwargs)

    async def _api_post(self, url, **kwargs):
        """
        A convenience wrapper for _post. Adds headers, auth and base url by
        default
        """
        kwargs['url'] = self.url + url
        kwargs['auth'] = self.auth

        headers = deepcopy(self.headers)
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers
        await self._post(**kwargs)

    async def _post(self, *args, **kwargs):
        """
        A wrapper for posting things. It will also json encode your 'data' parameter

        :returns: The response of your post
        :rtype: dict
        """
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data']).encode()

        async with aiohttp.ClientSession(**self.session_args) as session:
            await session.post(*args, **kwargs)

    async def _api_delete(self, url, **kwargs):
        """
        A convenience wrapper for _delete. Adds headers, auth and base url by
        default
        """
        kwargs['url'] = self.url + url
        kwargs['auth'] = self.auth

        headers = deepcopy(self.headers)
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        await self._delete(**kwargs)

    async def _delete(self, *args, **kwargs):
        """
        A wrapper for deleting things

        :returns: The response of your delete
        :rtype: dict
        """
        async with aiohttp.ClientSession(**self.session_args) as session:
            await session.delete(*args, **kwargs)
