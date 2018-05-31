##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

import json
import uuid

import pytest
from grappa import should

from pgadmin.browser.server_groups.servers.databases.schemas.tests import \
    utils as schema_utils
from pgadmin.utils.tests_helper import convert_response_to_json, \
    assert_json_values_from_response
from regression.python_test_utils import test_utils as utils
from . import utils as package_utils


@pytest.mark.skip_databases(['gpdb', 'pg'])
class TestPackagePut:
    @pytest.mark.usefixtures('require_database_connection')
    def test_package_put(self, context_of_tests):
        """
        When the package PUT request is send to the backend
        it returns 200 status
        """

        url = '/browser/package/obj/'

        http_client = context_of_tests['test_client']
        server = context_of_tests['server']
        server_data = context_of_tests['server_information']
        server_id = server_data['server_id']
        db_id = server_data['db_id']
        db_name = server_data['db_name']

        schema_name = server_data['schema_name']
        schema_id = server_data['schema_id']

        schema_response = schema_utils.verify_schemas(server,
                                                      db_name,
                                                      schema_name)
        if not schema_response:
            raise Exception('Could not find the schema.')

        pkg_name = 'pkg_%s' % str(uuid.uuid4())[1:4]
        proc_name = 'proc_%s' % str(uuid.uuid4())[1:4]
        package_id = package_utils.create_package(
            server,
            db_name,
            schema_name,
            pkg_name,
            proc_name)

        package_response = package_utils.verify_package(server,
                                                        db_name,
                                                        schema_name)

        if not package_response:
            raise Exception('Could not find the package.')

        data = {
            'description': 'This is FTS template update comment',
            'id': package_id
        }

        response = http_client.put(
            url + str(utils.SERVER_GROUP) + '/' +
            str(server_id) + '/' +
            str(db_id) + '/' +
            str(schema_id) + '/' +
            str(package_id),
            data=json.dumps(data),
            follow_redirects=True)

        response.status_code | should.be.equal.to(200)
        json_response = convert_response_to_json(response)
        assert_json_values_from_response(
            json_response,
            'package',
            'pgadmin.node.package',
            False,
            'icon-package',
            pkg_name
        )
