##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

import os

import pytest
from grappa import should

from regression.python_test_utils import test_utils
from regression.python_test_utils.template_helper import file_as_template


@pytest.mark.database
class TestDependenciesSql:
    def test_dependencies_sql(self, context_of_tests):
        """
        When all parameters are present
        It correctly generates the SQL
        And executes against the database
        """
        server = context_of_tests['server']
        with test_utils.Database(server) as (connection, database_name):
            test_utils.create_table(server, database_name, 'test_table')

            if connection.server_version < 90100:
                versions_to_test = ['default']
            else:
                versions_to_test = ['9.1_plus']

            cursor = connection.cursor()
            cursor.execute("SELECT pg_class.oid AS table_id "
                           "FROM pg_class "
                           "WHERE pg_class.relname='test_table'")
            table_id = cursor.fetchone()[0]

            for version in versions_to_test:
                template_file = self.get_template_file(
                    version,
                    'dependencies.sql')
                template = file_as_template(template_file)
                sql = template.render(
                    where_clause="WHERE dep.objid=%s::oid" % table_id)

                cursor = connection.cursor()
                cursor.execute(sql)
                fetch_result = cursor.fetchall()

                fetch_result | should.have.length(1)

                first_row = {}
                for index, description in enumerate(cursor.description):
                    first_row[description.name] = fetch_result[0][index]

                first_row['deptype'] | should.be.equal.to('n')
                first_row['refname'] | should.be.equal.to('public')

    @staticmethod
    def get_template_file(version, filename):
        return os.path.join(os.path.dirname(__file__), '..', 'templates',
                            'depends', 'sql', version, filename)
