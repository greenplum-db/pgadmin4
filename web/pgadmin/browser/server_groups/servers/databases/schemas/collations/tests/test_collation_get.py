##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

import uuid

import pytest
from grappa import should

from pgadmin.browser.server_groups.servers.databases.schemas.tests import \
    utils as schema_utils
from pgadmin.browser.server_groups.servers.databases.tests import utils as \
    database_utils
from pgadmin.utils.tests_helper import convert_response_to_json
from regression import parent_node_dict
from regression.python_test_utils import test_utils as utils
from . import utils as collation_utils


@pytest.mark.skip_databases(['gpdb'])
class TestCollationGet:
    def test_collation_get(self, request, context_of_tests):
        """
        When the collation get request is send to the backend
        it returns 200 status
        """
        request.addfinalizer(self.tearDown)

        url = '/browser/collation/obj/'

        self.server_data = parent_node_dict['database'][-1]
        self.tester = context_of_tests['test_client']
        self.server = context_of_tests['server']
        self.server_id = self.server_data['server_id']
        self.db_id = self.server_data['db_id']

        self.schema_info = parent_node_dict["schema"][-1]
        self.schema_name = self.schema_info["schema_name"]
        self.db_name = parent_node_dict["database"][-1]["db_name"]
        coll_name = "collation_get_%s" % str(uuid.uuid4())[1:8]
        self.collation = collation_utils.create_collation(self.server,
                                                          self.schema_name,
                                                          coll_name,
                                                          self.db_name)

        connection = utils.get_db_connection(self.db_name,
                                             self.server['username'],
                                             self.server['db_password'],
                                             self.server['host'],
                                             self.server['port'],
                                             self.server['sslmode'])
        self.schema_details = schema_utils.create_schema(connection,
                                                         self.schema_name)

        db_con = database_utils.connect_database(self,
                                                 utils.SERVER_GROUP,
                                                 self.server_id,
                                                 self.db_id)
        if not db_con["info"] == "Database connected.":
            raise Exception("Could not connect to database.")

        schema_response = schema_utils.verify_schemas(self.server,
                                                      self.db_name,
                                                      self.schema_name)
        if not schema_response:
            raise Exception("Could not find the schema to add the collation.")

        collation_id = self.collation[0]
        schema_id = self.schema_info["schema_id"]
        response = self.tester.get(
            url + str(utils.SERVER_GROUP) + '/' + str(
                self.server_id) + '/' +
            str(self.db_id) + '/' + str(schema_id) + '/' + str(collation_id),
            content_type='html/json')

        response.status_code | should.be.equal.to(200)
        json_response = convert_response_to_json(response)
        json_response | should.have.key('oid')
        json_response | should.have.key('name') > \
            should.be.equal.to(coll_name)
        json_response | should.have.key('description') > should.be.none
        json_response | should.have.key('schema') > should.be\
            .equal(self.schema_name)

    def tearDown(self):
        database_utils.client_disconnect_database(self.tester, self.server_id,
                                                  self.db_id)
