import md5, base64

from Products.CMFCore.utils import getToolByName
from zope import component
from zope import interface

from interfaces import IuPayStandardOptions, IuPayStandardProcessor

from getpaid.core import interfaces as GetPaidInterfaces

class uPayStandardProcessor( object ):
   
    interface.implements( IuPayStandardProcessor )

    options_interface = IuPayStandardOptions

    def __init__( self, context ):
        self.context = context

    def cart_post_button( self, order ):
        siteroot = getToolByName(self.context, "portal_url").getPortalObject()
        options = IuPayStandardOptions( siteroot )

        _button_form = """<form style="display:inline;" action="%(site)s" method="post" id="upay-button">
<input type="hidden" name="UPAY_SITE_ID" value="%(merchant_id)s" />
<input type="hidden" name="EXT_TRANS_ID" value="%(order_id)s" />
<input type="hidden" name="AMT" value="%(order_amount)s" />
<input type="hidden" name="VALIDATION_KEY" value="%(validation_key)s" />
<input type="submit" class="button context" name="checkout"/>
</form>
"""
        totalPrice = ("%.2f" % round(order.getTotalPrice(),2))
        
        formvals = {"site" : options.server_url,
                    "merchant_id": options.merchant_id,
                    "order_id" : order.order_id,
                    "order_amount": totalPrice,
                    "validation_key":base64.b64encode(md5.new(str(options.posting_key) + str(order.order_id) + str(totalPrice)).digest())
                   }
        return _button_form % formvals
    
    def capture(self, order, price):
        # always returns async - just here to make the processor happy
        return GetPaidInterfaces.keys.results_async

    def authorize( self, order, payment ):
        pass
