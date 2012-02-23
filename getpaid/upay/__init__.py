  # -*- extra stuff goes here -*- 
from getpaid.core.options import PersistentOptions
import interfaces

uPayStandardOptions = PersistentOptions.wire("uPayStandardOptions",
                                             "getpaid.upay",
                                             interfaces.IuPayStandardOptions)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
