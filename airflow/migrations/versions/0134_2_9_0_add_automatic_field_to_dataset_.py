#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""add automatic field to datasetevents table

Revision ID: a86bfaaf8266
Revises: 10b52ebd31f7
Create Date: 2023-12-11 17:05:52.688373

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a86bfaaf8266'
down_revision = '10b52ebd31f7'
branch_labels = None
depends_on = None
airflow_version = "2.9.0"


def upgrade():
    """Apply add automatic field to Dataset table"""
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("automatic", sa.Boolean(), default=False))


def downgrade():
    """Unapply add automatic field to Dataset table"""
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("automatic")
