# -*- coding: utf-8 -*-
import logging

from pyramid.interfaces import IRequest

from openregistry.lots.core.interfaces import IContentConfigurator, ILotManager
from openregistry.lots.core.traversal import Root, factory
from openregistry.lots.core.utils import add_related_processes_views

from openregistry.lots.loki.models import Lot, ILokiLot
from openregistry.lots.loki.adapters import LokiLotConfigurator, LokiLotManagerAdapter
from openregistry.lots.loki.migration import (
    LokiMigrationsRunner,
    MIGRATION_STEPS,
)
from openregistry.lots.loki.constants import (
    DEFAULT_LOT_TYPE,
    DEFAULT_LEVEL_OF_ACCREDITATION
)

LOGGER = logging.getLogger(__name__)


def includeme(config, plugin_config=None):
    config.scan("openregistry.lots.loki.views")
    config.scan("openregistry.lots.loki.subscribers")
    configurator = (LokiLotConfigurator, (ILokiLot, IRequest), IContentConfigurator)
    manager = (LokiLotManagerAdapter, (ILokiLot,), ILotManager)
    for adapter in (configurator, manager):
        config.registry.registerAdapter(*adapter)

    lot_types = plugin_config.get('aliases', [])
    if plugin_config.get('use_default', False):
        lot_types.append(DEFAULT_LOT_TYPE)
    for lt in lot_types:
        config.add_lotType(Lot, lt)
    LOGGER.info("Included openregistry.lots.loki plugin", extra={'MESSAGE_ID': 'included_plugin'})

    # migrate data
    if plugin_config.get('migration') is True:
        runner = LokiMigrationsRunner(config.registry.db)
        runner.migrate(MIGRATION_STEPS)

    # add accreditation level
    if not plugin_config.get('accreditation'):
        config.registry.accreditation['lot'][Lot._internal_type] = DEFAULT_LEVEL_OF_ACCREDITATION
    else:
        config.registry.accreditation['lot'][Lot._internal_type] = plugin_config['accreditation']
    # Related Processes
    add_related_processes_views(config, '/lots/{lot_id}', factory)
