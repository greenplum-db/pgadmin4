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
from pgadmin.utils.base_test_generator import BaseTestGenerator
from pgadmin.utils.tests_helper import convert_response_to_json
from regression import parent_node_dict
from regression.python_test_utils import test_utils as utils
from . import utils as sequence_utils


@pytest.mark.skip_databases(['gpdb'])
class TestSequenceGet:
    def test_sequence_get(self, request, context_of_tests):
        """
        When the sequence get request is send to the backend
        it returns 200 status
        """
        request.addfinalizer(self.tearDown)

        url = '/browser/sequence/obj/'

        self.tester = context_of_tests['test_client']
        self.server = context_of_tests['server']
        self.server_data = parent_node_dict['database'][-1]
        self.server_id = self.server_data['server_id']
        self.db_id = self.server_data['db_id']
        self.db_name = self.server_data['db_name']

        self.schema_info = parent_node_dict['schema'][-1]
        self.schema_name = self.schema_info['schema_name']
        self.schema_id = self.schema_info['schema_id']

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
            raise Exception("Could not find the schema.")

        sequence_name = "test_sequence_delete_%s" % str(uuid.uuid4())[1:8]
        self.sequence_id = sequence_utils.create_sequences(
            self.server,
            self.db_name,
            self.schema_name,
            sequence_name
        )

        response = self.tester.get(
            url + str(utils.SERVER_GROUP) + '/' +
            str(self.server_id) + '/' +
            str(self.db_id) + '/' +
            str(self.schema_id) + '/' +
            str(self.sequence_id),
            follow_redirects=True)

        response.status_code | should.be.equal.to(200)
        json_response = convert_response_to_json(response)
        json_response | should.have.key('oid')
        json_response | should.have.key('name') > \
            should.be.equal.to(sequence_name)

    def tearDown(self):
        database_utils.client_disconnect_database(self.tester, self.server_id,
                                                  self.db_id)
