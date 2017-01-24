"""
#----------------------------------------------------------------------
#    This file is part of "Soft Cluster EX"
#    and covered by a BSD-style license, check
#    LICENSE for detail.
#
#    Author:      Webber Huang
#    Contact:     xracz.fx@gmail.com
#    Homepage:    http://riggingtd.com
#----------------------------------------------------------------------
"""

__author__ = 'Webber Huang <xracz.fx@gmail.com>'
__website__ = 'http://riggingtd.com/downloads/soft-cluster-ex/'
__license__ = 'BSD license'

def launch():
    import startup.setup as setup
    reload(setup)
    setup.launch()