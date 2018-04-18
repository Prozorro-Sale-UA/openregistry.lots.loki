# -*- coding: utf-8 -*-
from uuid import uuid4
from copy import deepcopy
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types import StringType, IntType, URLType, MD5Type
from schematics.types.compound import ModelType, ListType
from schematics.types.serializable import serializable
from zope.interface import implementer

from openregistry.lots.core.models import (
    Value
)
from openregistry.lots.core.models import (
    Guarantee,
    Period
)

from openregistry.lots.core.models import (
    Classification,
    LokiDocument as Document,
    LokiItem as Item,
    Decision,
    AssetCustodian,
    AssetHolder
)
from openregistry.lots.core.models import (
    Model,
    IsoDateTimeType,
    IsoDurationType,
)
from openregistry.lots.core.constants import IDENTIFIER_CODES
from openregistry.lots.core.models import ILot, Lot as BaseLot
from openregistry.lots.core.utils import (
    get_now,
    calculate_business_date
)

from .constants import LOT_STATUSES, RECTIFICATION_PERIOD_DURATION
from .roles import (
    lot_roles,
    lot_edit_role
)


class ILokiLot(ILot):
    """ Marker interface for basic lots """


class StartDateRequiredPeriod(Period):
    startDate = IsoDateTimeType(required=True)


class UAEDRAndMFOClassification(Classification):
    scheme = StringType(choices=['UA-EDR', 'MFO'], required=True)


class AccountDetails(Model):
    description = StringType()
    bankName = StringType()
    accountNumber = StringType()
    additionalClassifications = ListType(ModelType(UAEDRAndMFOClassification), default=list())


class Auction(Model):
    id = StringType()
    auctionID = StringType()
    procurementMethodType = StringType(choices=['Loki.english', 'Loki.insider'])
    auctionPeriod = ModelType(StartDateRequiredPeriod, required=True)
    tenderingDuration = IsoDurationType(required=True)
    documents = ListType(ModelType(Document))
    value = ModelType(Value, required=True)
    minimalStep = ModelType(Value, required=True)
    guarantee = ModelType(Guarantee, required=True)
    registrationFee = ModelType(Guarantee)
    accountDetails = ModelType(AccountDetails)
    dutchSteps = IntType(default=None, min_value=1, max_value=100)

    def validate_dutchSteps(self, data, value):
        if value and data['procurementMethodType'] != 'Loki.insider':
            raise ValidationError('Field dutchSteps is allowed only when procuremenentMethodType is Loki.insider')
        if data['procurementMethodType'] == 'Loki.insider' and not value:
            data['dutchSteps'] = 99 if data.get('dutchSteps') is None else data['dutchSteps']


@implementer(ILokiLot)
class Lot(BaseLot):
    class Options:
        roles = lot_roles

    title = StringType()
    status = StringType(choices=LOT_STATUSES, default='draft')
    description = StringType()
    lotType = StringType(default="loki")
    rectificationPeriod = ModelType(Period)
    lotCustodian = ModelType(AssetCustodian, serialize_when_none=False)
    lotHolder = ModelType(AssetHolder, serialize_when_none=False)
    officialRegistrationID = StringType(serialize_when_none=False)
    items = ListType(ModelType(Item), default=list())
    documents = ListType(ModelType(Document), default=list())
    decisions = ListType(ModelType(Decision), default=list(), max_size=2)
    assets = ListType(MD5Type(), required=True, min_size=1, max_size=1)
    auctions = ListType(ModelType(Auction), max_size=3, min_size=3, required=True)

    def __init__(self, *args, **kwargs):
        super(Lot, self).__init__(*args, **kwargs)
        if self.rectificationPeriod and self.rectificationPeriod.endDate < get_now():
            self._options.roles['edit_pending'] = whitelist('status')
        else:
            self._options.roles['edit_pending'] = lot_edit_role

    def validate_auctions(self, data, value):
        if not value:
            return
        full_price = value[0].value.amount
        price_range = (round(full_price/2), full_price/2) if round(full_price/2) < full_price/2 else (full_price/2, round(full_price/2))
        if not (value[1].value.amount >= price_range[0] and value[1].value.amount <= price_range[1]):
            raise ValidationError('In second loki.english value.amount must be a half of value.amount first loki.english')
        if value[0].value.amount != value[2].value.amount:
            raise ValidationError('Loki.english and Loki.insider must have same value.amount')
        data['auctions'][0]['procurementMethodType'] = 'Loki.english'
        data['auctions'][1]['procurementMethodType'] = 'Loki.english'
        data['auctions'][2]['procurementMethodType'] = 'Loki.insider'

    @serializable(serialized_name='rectificationPeriod', serialize_when_none=False)
    def serialize_rectificationPeriod(self):
        if self.status == 'pending' and not self.rectificationPeriod:
            self.rectificationPeriod = type(self).rectificationPeriod.model_class()
            self.rectificationPeriod.startDate = get_now()
            self.rectificationPeriod.endDate = calculate_business_date(self.rectificationPeriod.startDate,
                                                                       RECTIFICATION_PERIOD_DURATION)

    def validate_status(self, data, value):
        can_be_deleted = any([doc.documentType == 'cancellationDetails' for doc in data['documents']])
        if value == 'deleted' and not can_be_deleted:
            raise ValidationError(u"You can set deleted status "
                                  u"only when asset have at least one document with \'cancellationDetails\' documentType")

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_lot'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_lot_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_lot_items'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_lot_publications'),
        ]
        return acl
