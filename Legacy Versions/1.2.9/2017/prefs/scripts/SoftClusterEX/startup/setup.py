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


__author__              = 'Webber Huang'
__buildVersionID__      = '3.0.1'
__website__             = 'http://riggingtd.com/downloads/soft-cluster-ex/'
__license__             = 'BSD license'
__BANNER__              = 'softClusterEXBanner.png'
__BANNER_JOINT__        = 'softClusterEXBannerJ.png'
__ICON__                = 'softClusterEXIcon.png'

__SUPPORTTYPE_LABEL__ = {'mesh': 'Polygon',
                         'nurbsSurface': 'Surface',
                         'nurbsCurve': 'Curve',
                         'subdiv': 'Subdivision',
                         'lattice': 'Lattice'}

__ENVIRONMENT_NAME__ = "SOFT_CLUSTER_EX"

import sys
import os
import maya.cmds as cmds
import maya.mel as mel

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

#----------------------------------------------------------------------
def loadPlugin():
    """
    load softSelectionQuery plugin
    """
    
    mayaVers = int(mayaVersion())
    os = cmds.about(os=1)
    
    if os == 'win64':
        pluginName = 'softSelectionQuery.mll'
    elif os == 'mac':
        pluginName = 'softSelectionQuery.bundle'
    elif os == 'linux64':
        pluginName = 'softSelectionQuery.so'
    else:
        cmds.error('Soft Cluster EX is available for 64bit version of Autodesk Maya 2011 '
                  'or above under Windows 64bit, Mac OS X and Linux 64bit!')
    
    if not cmds.pluginInfo(pluginName, q=True, l=True ):
        cmds.loadPlugin(pluginName)
        version = cmds.pluginInfo(pluginName, q=1, v=1)
        log.info('Plug-in: %s v%s loaded success!' % (pluginName, version))
    else:
        version = cmds.pluginInfo(pluginName, q=1, v=1)
        log.info('Plug-in: %s v%s has been loaded!' % (pluginName, version))

#----------------------------------------------------------------------
def show():
    """"""
    from SoftClusterEX.ui import mainWindow
    reload(mainWindow)
    mainWindow.MainWindow()

def getBanner():
    """Constructor"""
    path = os.path.join(getModulePath(), 'icons')
    return os.path.join(path, __BANNER__)

def getBannerJ():
    """Constructor"""
    path = os.path.join(getModulePath(), 'icons')
    return os.path.join(path, __BANNER_JOINT__)

def getIcon():
    """Constructor"""
    path = os.path.join(getModulePath(), 'icons')
    return os.path.join(path, __ICON__)

#----------------------------------------------------------------------
def getSupportTypes():
    """
    Returns:
      dict
    """
    return __SUPPORTTYPE_LABEL__

#----------------------------------------------------------------------
def getEnviron():
    """"""
    return __ENVIRONMENT_NAME__
    
"""
#----------------------------------------------------------------------
# Codes below comes from part of Red9 StudioTools:
# https://github.com/markj3d/Red9_StudioPack/blob/master/startup/setup.py
# I make a slightly modification to meet my own demands.
# Thanks, Mark Jackson.
#----------------------------------------------------------------------
"""
#----------------------------------------------------------------------
def mayaVersion():
    #need to manage this better and use the API version,
    #eg: 2013.5 returns 2013
    return mel.eval('getApplicationVersionAsFloat')

# General Pack Data --------------------------------------------------------------------
    
def getModulePath():
    '''
    Returns the Main path to the root module folder
    '''
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),'')

def getPackagePath():
    '''
    Returns the Main path to the root package folder
    '''
    return os.path.join(os.path.dirname(os.path.dirname(__file__)),'')

def openBlog():
    '''
    open up the Soft Cluster Blog
    '''
    from SoftClusterEX.core import scUtil
    scUtil.os_OpenFile(__website__)
    
def getVersion():
    return __buildVersionID__

def getAuthor():
    return __author__

  
# BOOT FUNCTS - Add and Build --------------------------------------------------------------
    
def addScriptsPath(path):
    '''
    Add additional folders to the ScriptPath
    '''
    scriptsPath = os.environ.get('MAYA_SCRIPT_PATH')
    
    if os.path.exists(path):
        if not path in scriptsPath:
            log.info('Adding To Script Paths : %s' % path)
            os.environ['MAYA_SCRIPT_PATH']+='%s%s' % (os.pathsep, path)
        else:
            log.info('Soft Cluster EX Script Path already setup : %s' % path)
    else:
        log.debug('Given Script Path is invalid : %s' % path)

def addPluginPath():
    '''
    Make sure the plugin path has been added. If run as a module
    this will have already been added
    '''
    path = os.path.join(getPackagePath(), 'plug-ins')
    plugPaths = os.environ.get('MAYA_PLUG_IN_PATH')
    
    if not path in plugPaths:
        log.info('Adding Soft Cluster EX Plug-ins to Plugin Paths : %s' % path)
        os.environ['MAYA_PLUG_IN_PATH'] += '%s%s' % (os.pathsep, path)
    else:
        log.info('Soft Cluster EX Plug-in Path already setup')
              
def addIconsPath():
    '''
    Make sure the icons path has been added. If run as a module
    this will have already been added
    '''
    path = os.path.join(getModulePath(), 'icons')
    iconsPath = os.environ.get('XBMLANGPATH')
    
    if not path in iconsPath:
        log.info('Adding Soft Cluster EX Icons To XBM Paths : %s' % path)
        os.environ['XBMLANGPATH'] += '%s%s' % (os.pathsep, path)
    else:
        log.info('Soft Cluster EX Icons Path already setup')



#=========================================================================================
# BOOT CALL ------------------------------------------------------------------------------
#=========================================================================================
    
def launch():
    '''
    Main entry point for the Soft Cluster EX
    '''
    log.info('Soft Cluster EX v%s : author: %s' % (getVersion(), getAuthor()))
    log.info('Soft Cluster EX Setup Calls :: Booting from >> %s' % getPackagePath())
    
    # Ensure the Plug-in and Icon paths are up
    #addPluginPath()
    #addIconsPath()
    
    # Add module to environment
    os.environ[__ENVIRONMENT_NAME__] = getPackagePath()
    
    # Load Plug-in
    loadPlugin()
    
    # launch UI
    show()
    
    log.info('Soft Cluster EX Complete!')

"""
#----------------------------------------------------------------------
# Codes below comes from part of Red9 StudioTools:
# https://github.com/markj3d/Red9_StudioPack/blob/master/startup/setup.py
# I make a slightly modification to meet my own demands.
# Thanks, Mark Jackson.
#----------------------------------------------------------------------
"""