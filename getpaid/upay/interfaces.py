from getpaid.core import interfaces
from zope import schema

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid.upay')

class IuPayStandardProcessor( interfaces.IPaymentProcessor ):
    """uPay Standard Processor
    """

class IuPayStandardOptions( interfaces.IPaymentProcessorOptions ):
    """uPay Standard Options
    """
    server_url = schema.ASCIILine( title = _(u"uPay Site URL"))
    merchant_id = schema.ASCIILine( title = _(u"uPay Id"))
    posting_key = schema.ASCIILine( title = _(u"uPay Posting key"))

