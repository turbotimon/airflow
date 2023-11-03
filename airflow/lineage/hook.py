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
from __future__ import annotations

import typing

from sqlalchemy import select
from sqlalchemy.sql import expression

from airflow.compat.functools import cache
from airflow.datasets.manager import dataset_manager
from airflow.models.dataset import DatasetModel
from airflow.utils.module_loading import import_string
from airflow.utils.session import NEW_SESSION, provide_session

if typing.TYPE_CHECKING:
    from airflow.datasets import Dataset
    from airflow.hooks.base import BaseHook


class LineageCollector:
    """Info."""

    def __init__(self):
        self.inputs: list[tuple[Dataset, BaseHook]] = []
        self.outputs: list[tuple[Dataset, BaseHook]] = []

    def add_input(self, dataset: Dataset, hook: BaseHook):
        self.inputs.append((dataset, hook))

    def add_output(self, dataset: Dataset, hook: BaseHook):
        self.outputs.append((dataset, hook))

    @property
    def collected(self) -> tuple[list[tuple[Dataset, BaseHook]], list[tuple[Dataset, BaseHook]]]:
        return self.inputs, self.outputs

    def has_collected(self) -> bool:
        return len(self.inputs) != 0 and len(self.outputs) != 0

    @provide_session
    def emit_datasets(self, session=NEW_SESSION):
        all_datasets = self.inputs + self.outputs
        # store datasets
        stored_datasets: dict[str, DatasetModel] = {}
        new_datasets: list[DatasetModel] = []
        for dataset, hook in all_datasets:
            stored_dataset = session.scalar(
                select(DatasetModel).where(DatasetModel.uri == dataset.uri).limit(1)
            )
            if stored_dataset:
                # Some datasets may have been previously unreferenced, and therefore orphaned by the
                # scheduler. But if we're here, then we have found that dataset again in our DAGs, which
                # means that it is no longer an orphan, so set is_orphaned to False.
                stored_dataset.is_orphaned = expression.false()
                stored_datasets[stored_dataset.uri] = stored_dataset
            else:
                new_datasets.append(DatasetModel.from_public(dataset))
        dataset_manager.create_datasets(dataset_models=new_datasets, session=session)


_collector = LineageCollector()


@cache
def does_openlineage_exist() -> bool:
    is_disabled = import_string("apache.airflow.providers.openlineage.plugin._is_disabled")
    return is_disabled and is_disabled()


def get_hook_lineage_collector() -> LineageCollector:
    return _collector
