#   Copyright Peznauts <kevin@cloudnull.com>. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import unittest
from unittest.mock import patch

import redis

from directord.datastores import redis as datastore_redis


class TestDatastoreInternal(unittest.TestCase):
    def setUp(self):
        self.log_patched = patch("directord.logger.getLogger")
        self.log = self.log_patched.start()
        self.redis_patched = patch.object(
            redis.Redis, "from_url", autospec=True
        )
        self.redis_patched.start()
        self.datastore = datastore_redis.BaseDocument(
            url="redis://test.localdomain"
        )

    def tearDown(self):
        self.log_patched.stop()
        self.redis_patched.stop()

    def test___getitem__string(self):
        self.datastore.__getitem__(key="test")

    def test___setitem__(self):
        self.datastore.__setitem__(key="key", value="value")

    def test___delitem__(self):
        self.datastore.__delitem__(key="key")

    def test_items(self):
        self.datastore.items()

    def test_keys(self):
        self.datastore.keys()

    def test_empty(self):
        self.datastore.empty()

    def test_pop(self):
        self.datastore.pop(key="key")

    def test_prune(self):
        self.datastore.prune()

    def test_get(self):
        self.datastore.get(key="key")

    def test_set(self):
        self.datastore.set(key="key", value="value")
