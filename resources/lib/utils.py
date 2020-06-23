import xbmc
import xbmcaddon

ADDON_ID = 'service.autoambilight'
ADDON = xbmcaddon.Addon(ADDON_ID)
CWD = ADDON.getAddonInfo('path').decode('utf-8')

def log(message, loglevel=xbmc.LOGNOTICE):
    xbmc.log(encode(ADDON_ID+ "-" + ADDON.getAddonInfo('version') + " : " + message), level=loglevel)

def encode(string):
    return string.encode('UTF-8', 'replace')
