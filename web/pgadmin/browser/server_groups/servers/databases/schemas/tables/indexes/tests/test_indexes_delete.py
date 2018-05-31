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

from pgadmin.browser.server_groups.servers.databases.schemas.tables.column. \
    tests import utils as columns_utils
from pgadmin.browser.server_groups.servers.databases.schemas.tables.tests \
    import utils as tables_utils
from pgadmin.browser.server_groups.servers.databases.schemas.tests import \
    utils as schema_utils
from pgadmin.utils.tests_helper import convert_response_to_json
from regression.python_test_utils import test_utils as utils
from . import utils as indexes_utils


class TestIndexesDelete:
    @pytest.mark.usefixtures('require_database_connection')
    def test_synonym_delete(self, context_of_tests):
        """
        When the Index DELETE request is send to the backend
        it returns 200 status
        """
        http_client = context_of_tests['test_client']
        server = context_of_tests['server']
        server_data = context_of_tests['server_information']

        db_name = server_data['db_name']
        server_id = server_data['server_id']
        db_id = server_data['db_id']
        schema_id = server_data['schema_id']
        schema_name = server_data['schema_name']
        schema_response = schema_utils.verify_schemas(server,
                                                      db_name,
                                                      schema_name)
        if not schema_response:
            raise Exception('Could not find the schema to add a table.')
        table_name = 'table_column_%s' % (str(uuid.uuid4())[1:8])
        table_id = tables_utils.create_table(server, db_name,
                                             schema_name,
                                             table_name)
        column_name = 'test_column_delete_%s' % (str(uuid.uuid4())[1:8])
        columns_utils.create_column(server,
                                    db_name,
                                    schema_name,
                                    table_name,
                                    column_name)
        index_name = 'test_index_delete_%s' % (str(uuid.uuid4())[1:8])
        index_id = indexes_utils.create_index(server, db_name,
                                              schema_name,
                                              table_name,
                                              index_name,
                                              column_name)

        index_response = indexes_utils.verify_index(server, db_name,
                                                    index_name)
        if not index_response:
            raise Exception('Could not find the index to delete.')

        url = '/browser/index/obj/'
        response = http_client.delete(url + str(utils.SERVER_GROUP) +
                                      '/' + str(server_id) + '/' +
                                      str(db_id) + '/' +
                                      str(schema_id) + '/' +
                                      str(table_id) + '/' +
                                      str(index_id),
                                      follow_redirects=True)

        response.status_code | should.be.equal.to(200)
        json_response = convert_response_to_json(response)
        json_response | should.have.key('info') > should.be.equal.to(
            'Index is dropped')
        json_response | should.have.key('errormsg') > should.be.empty
        json_response | should.have.key('data')
        json_response | should.have.key('result') > should.be.none
        json_response | should.have.key('success') > should.be.equal.to(1)
