##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

from __future__ import print_function

import json
import uuid

import pytest
from grappa import should

from pgadmin.browser.server_groups.servers.databases.extensions.tests import \
    utils as extension_utils
from pgadmin.browser.server_groups.servers.databases.foreign_data_wrappers. \
    tests import utils as fdw_utils
from pgadmin.browser.server_groups.servers.databases.tests import \
    utils as database_utils
from regression.python_test_utils import test_utils as utils
from . import utils as fsrv_utils


@pytest.mark.skip_databases(['gpdb'])
class TestForeignServerPut:
    def test_foreign_server_get(self, request, context_of_tests):
        """
        When sending a HTTP request to get foreign server under database node
        It returns 200 status
        """

        request.addfinalizer(self.tearDown)

        url = '/browser/foreign_server/obj/'

        schema_data = context_of_tests['server_information']
        self.server = context_of_tests['server']
        self.server_id = schema_data['server_id']
        self.db_id = schema_data['db_id']
        self.db_name = schema_data['db_name']
        schema_name = schema_data['schema_name']
        self.extension_name = 'cube'
        fdw_name = "fdw_%s" % (str(uuid.uuid4())[1:8])
        fsrv_name = "test_fsrv_put_%s" % (str(uuid.uuid4())[1:8])
        extension_utils.create_extension(
            self.server, self.db_name, self.extension_name, schema_name)
        fdw_id = fdw_utils.create_fdw(self.server, self.db_name,
                                      fdw_name)
        fsrv_id = fsrv_utils.create_fsrv(self.server, self.db_name,
                                         fsrv_name, fdw_name)

        self.tester = context_of_tests['test_client']

        db_con = database_utils.client_connect_database(
            self.tester,
            utils.SERVER_GROUP,
            self.server_id,
            self.db_id,
            self.server['db_password'])

        db_con["info"] | should.be.equal.to(
            'Database connected.',
            msg='Could not connect to database.')

        fdw_utils.verify_fdw(self.server, self.db_name, fdw_name) | \
            should.not_be.equal.to(None, msg='Could not find FDW.')

        fsrv_utils.verify_fsrv(self.server, self.db_name, fsrv_name) | \
            should.not_be.equal.to(None, msg='Could not find FSRV.')

        data = {"description": "This is foreign server update comment",
                "id": fsrv_id}

        put_response = self.tester.put(
            url + str(utils.SERVER_GROUP) + '/' +
            str(self.server_id) + '/' + str(self.db_id) +
            '/' + str(fdw_id) + '/' +
            str(fsrv_id), data=json.dumps(data),
            follow_redirects=True)

        put_response.status_code | should.be.equal.to(200)

    def tearDown(self):
        extension_utils.drop_extension(self.server, self.db_name,
                                       self.extension_name)
        database_utils.client_disconnect_database(
            self.tester, self.server_id, self.db_id)
