from asynctest import PropertyMock, MagicMock


class AsyncContextManagerMock(MagicMock):
    async def __aenter__(self):
        return self.aenter

    async def __aexit__(self, *args):
        pass


class AsyncContextManagerMockPagination(MagicMock):
    async def __aenter__(self):
        return self.aenter

    async def __aexit__(self, *args):
        pass

    # two pages
    headers = PropertyMock(side_effect=[{'cb-after': 123}, {}])
