import logging

import re

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getUtility

from getpaid.core.interfaces import IOrderManager

from getpaid.upay.interfaces import IuPayStandardOptions

logger = logging.getLogger("getpaid.upay")

class Listener(BrowserView):
    """Listener for uPay notifications - registered as a page view
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()
    
    def process(self):
        options = IuPayStandardOptions( self.portal )

        order_manager = getUtility(IOrderManager)
        if self.request['EXT_TRANS_ID'] in order_manager:
            order = order_manager.get(self.request['EXT_TRANS_ID'])
            if self.request['pmt_status'] == 'success':
                self.fill_in_order_data(order)
                order.finance_workflow.fireTransition('charge-charging')
                logger.info('received successful payment notification for order %s' % self.request['EXT_TRANS_ID'])
            elif self.request['pmt_status'] == 'cancelled':
                order.finance_workflow.fireTransition('decline-charging')
                logger.info('received unsuccessful payment notification for order %s' % self.request['EXT_TRANS_ID'])
            else:
                # notification not of interest to us right now
                logger.info('received notification for order %s that is not of interest - payment_status "%s"' % (self.request['EXT_TRANS_ID'], self.request['pmt_status']))
        else:    
            # invoice not in cart
            logger.info('received notification that does not apply to any order number - invoice "%s"' % self.request['EXT_TRANS_ID']) 

    def fill_in_order_data(self, order):
        if 'sys_tracking_id' in self.request.keys():
            order.processor_order_id = self.request['sys_tracking_id']
        
        if 'name_on_acct' in self.request.keys():
            order.contact_information.name = self.request['name_on_acct']
        
        if 'acct_email_address' in self.request.keys():
            order.contact_information.email = self.request['acct_email_address']
        
        if 'acct_phone_night' in self.request.keys():
            order.contact_information.phone_number = re.sub('[^\d]+', '', self.request['acct_phone_night'])
        if 'acct_phone_day' in self.request.keys():
            order.contact_information.phone_number = re.sub('[^\d]+', '', self.request['acct_phone_day'])    
        
        if 'acct_addr' in self.request.keys():
            order.billing_address.bill_first_line = self.request['acct_addr']

        if 'acct_addr2' in self.request.keys():
            order.billing_address.bill_second_line = self.request['acct_addr2']
        
        if 'acct_city' in self.request.keys():
            order.billing_address.bill_city = self.request['acct_city']
        
        if 'acct_state' in self.request.keys():
            order.billing_address.bill_state = self.request['acct_state']

        if 'acct_zip' in self.request.keys():
            order.billing_address.bill_postal_code = self.request['acct_zip']

        # mark address as same - uPay does not provide seperate shipping address, or country
        order.shipping_address.ship_same_billing = True
        order.billing_address.bill_country = 'UNITED STATES'