# Copyright 2015 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy

import testtools
from testtools import matchers

from magnumclient.tests import utils
from magnumclient.v1 import baymodels


BAYMODEL1 = {'id': 123,
             'uuid': '66666666-7777-8888-9999-000000000001',
             'name': 'baymodel1',
             'image_id': 'baymodel1-image',
             'flavor_id': 'm1.small',
             'keypair_id': 'keypair1',
             'external_network_id': 'd1f02cfb-d27f-4068-9332-84d907cb0e21',
             'dns_nameserver': '8.8.1.1',
             }
BAYMODEL2 = {'id': 124,
             'uuid': '66666666-7777-8888-9999-000000000002',
             'name': 'baymodel2',
             'image_id': 'baymodel2-image',
             'flavor_id': 'm2.small',
             'keypair_id': 'keypair2',
             'external_network_id': 'd1f02cfb-d27f-4068-9332-84d907cb0e22',
             'dns_nameserver': '8.8.1.2',
             }

CREATE_BAYMODEL = copy.deepcopy(BAYMODEL1)
del CREATE_BAYMODEL['id']
del CREATE_BAYMODEL['uuid']

UPDATED_BAYMODEL = copy.deepcopy(BAYMODEL1)
NEW_NAME = 'newbay'
UPDATED_BAYMODEL['name'] = NEW_NAME

fake_responses = {
    '/v1/baymodels':
    {
        'GET': (
            {},
            {'baymodels': [BAYMODEL1, BAYMODEL2]},
        ),
        'POST': (
            {},
            CREATE_BAYMODEL,
        ),
    },
    '/v1/baymodels/%s' % BAYMODEL1['id']:
    {
        'GET': (
            {},
            BAYMODEL1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_BAYMODEL,
        ),
    },
}


class BayModelManagerTest(testtools.TestCase):

    def setUp(self):
        super(BayModelManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = baymodels.BayModelManager(self.api)

    def test_baymodel_list(self):
        baymodels = self.mgr.list()
        expect = [
            ('GET', '/v1/baymodels', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(baymodels, matchers.HasLength(2))

    def test_baymodel_show(self):
        baymodel = self.mgr.get(BAYMODEL1['id'])
        expect = [
            ('GET', '/v1/baymodels/%s' % BAYMODEL1['id'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(BAYMODEL1['name'], baymodel.name)
        self.assertEqual(BAYMODEL1['image_id'], baymodel.image_id)

    def test_baymodel_create(self):
        baymodel = self.mgr.create(**CREATE_BAYMODEL)
        expect = [
            ('POST', '/v1/baymodels', {}, CREATE_BAYMODEL),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(baymodel)

    def test_baymodel_delete(self):
        baymodel = self.mgr.delete(BAYMODEL1['id'])
        expect = [
            ('DELETE', '/v1/baymodels/%s' % BAYMODEL1['id'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(baymodel)

    def test_baymodel_update(self):
        patch = {'op': 'replace',
                 'value': NEW_NAME,
                 'path': '/name'}
        baymodel = self.mgr.update(id=BAYMODEL1['id'], patch=patch)
        expect = [
            ('PATCH', '/v1/baymodels/%s' % BAYMODEL1['id'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_NAME, baymodel.name)