from Products.Five.browser import BrowserView
from zope.component import getUtility

from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions
from getpaid.core.interfaces import IShoppingCartUtility, IOrderManager
from getpaid.core.order import Order
from getpaid.core import payment

from cPickle import loads, dumps
from AccessControl import getSecurityManager

from getpaid.upay.upay import uPayStandardProcessor

class uPayButtonView(BrowserView):
    """page for upay button
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def getButton(self):
        button = uPayStandardProcessor(self.context)
        cart_util = getUtility(IShoppingCartUtility)
        cart = cart_util.get(self.context, create=True)
        site = self.context.portal_url.getPortalObject()
        manage_options = IGetPaidManagementOptions( site )
        
        # we'll get the order_manager, create the new order, and store it.
        order_manager = getUtility(IOrderManager)
        new_order_id = order_manager.newOrderId()
        order = Order()
        
        # register the payment processor name to make the workflow handlers happy
        order.processor_id = manage_options.payment_processor
        
        order.contact_information = payment.ContactInformation()
        order.billing_address = payment.BillingAddress()
        order.shipping_address = payment.ShippingAddress()

        order.order_id = new_order_id
        
        # make cart safe for persistence by using pickling
        order.shopping_cart = loads(dumps(cart))
        order.user_id = getSecurityManager().getUser().getId()

        order.finance_workflow.fireTransition('create')
        
        order_manager.store(order)

        # have to wait for the order to be created and the cart added for this to work
        order.finance_workflow.fireTransition('authorize')

        # save html for button - we'll destroy the cart later on
        html = button.cart_post_button(order)
        
        # and destroy the cart
        cart_util.destroy(self.context)

        return html
        
