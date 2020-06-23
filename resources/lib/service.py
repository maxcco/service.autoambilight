import json
import os
import xbmc
import xbmcaddon
from requests.auth import HTTPDigestAuth
import pylips
import utils

__addon__ = xbmcaddon.Addon()
__cwd__ = __addon__.getAddonInfo('path')
__profile__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))
__resource__ = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib'))


ADDON_ID = 'service.autoambilight'

# Built-in POST commands (basically wrappers around common API calls)
available_commands_post = json.load(open(__resource__ + '/commands.json', 'r'))



class ScreensaverMonitor(xbmc.Monitor):

    def __init__(self):
        xbmc.Monitor.__init__(self)

    def onScreensaverActivated(self):
        utils.log("screen saver on", xbmc.LOGDEBUG)
        AmbilightController.screensaver_state = True

    def onScreensaverDeactivated(self):
        utils.log("screen saver off", xbmc.LOGDEBUG)
        AmbilightController.screensaver_state = False

class PlayerMonitor(xbmc.Player):

    def __init__(self):
        xbmc.Player.__init__(self)
  
    def onPlayBackStarted(self):
        utils.log("play", xbmc.LOGDEBUG)
        if self.isPlayingVideo():
            AmbilightController.content = "MOVIE"
            utils.log(AmbilightController.content)
        else:
            AmbilightController.content = "MUSIC"
            utils.log(AmbilightController.content)
        AmbilightController.player_state = "play"

    def onPlayBackStopped(self):
        utils.log("stop", xbmc.LOGDEBUG)
        AmbilightController.player_state = "stop"

    def onPlayBackPaused(self):
        utils.log("pause", xbmc.LOGDEBUG)
        AmbilightController.player_state = "pause"

    def onPlayBackResume(self):
        utils.log("resume", xbmc.LOGDEBUG)
        AmbilightController.player_state = "play"

    def onPlayBackEnded(self):
        utils.log("end", xbmc.LOGDEBUG)
        AmbilightController.player_state = "stop"

def ambilight_switch(state):

    addon = xbmcaddon.Addon(ADDON_ID)
    ambilight_movie_mode = addon.getSetting('ambilight_movie_mode')
    ambilight_music_mode = addon.getSetting('ambilight_music_mode')
    ambilight_music = addon.getSetting('ambilight_music')


    config = {}
    config["api_version"] = addon.getSetting('api_version')
    config['user'] = addon.getSetting('user')
    config['pass'] = addon.getSetting('pass')
    config['address'] = addon.getSetting('tv_ipaddress')
    config['api_port'] = addon.getSetting('api_port')
    config['api_protocol'] = addon.getSetting('api_protocol')
    config['auth'] = HTTPDigestAuth(config['user'], config['pass'])

    if state:
        if AmbilightController.content == "MOVIE":
            config['path'] = available_commands_post["ambilight_video_"+ambilight_movie_mode]['path']
            config['body'] = available_commands_post["ambilight_video_"+ambilight_movie_mode]['body']
            pylips.post(config)
            utils.log(AmbilightController.content + " ambilight ON")

        if ambilight_music == "True" and AmbilightController.content == "MUSIC":
            config['path'] = available_commands_post["ambilight_audio_"+ambilight_music_mode]['path']
            config['body'] = available_commands_post["ambilight_audio_"+ambilight_music_mode]['body']
            pylips.post(config)
            utils.log(AmbilightController.content + " ambilight ON")
    else:
        config['path'] = available_commands_post["ambilight_off"]['path']
        config['body'] = available_commands_post["ambilight_off"]['body']
        pylips.post(config)
        utils.log("ambilight OFF")

def ambilight_update(player_state, screensaver_state):

    addon = xbmcaddon.Addon(ADDON_ID)
    ambilight_screensaver_setting = addon.getSetting('ambilight_screensaver')

    if player_state == "play":
        ambilight_switch(True)
    elif player_state == "pause" and not screensaver_state and ambilight_screensaver_setting == "True":
        ambilight_switch(True)
    else:
        ambilight_switch(False)


class AmbilightController():
    screensaver_monitor = None
    player_monitor = None
    player_state = "stop"
    player_prev_state = "stop"
    screensaver_state = False
    screensaver_prev_state = False
    content = "MOVIE"

    def __init__(self):
        self.player_monitor = PlayerMonitor()
        self.screensaver_monitor = ScreensaverMonitor()


    def runProgram(self):      
        while not xbmc.abortRequested:
            if (self.player_state != self.player_prev_state or self.screensaver_state != self.screensaver_prev_state):
                ambilight_update(self.player_state, self.screensaver_state)
                self.screensaver_prev_state = self.screensaver_state
                self.player_prev_state = self.player_state
            xbmc.sleep(500)

        #clean up monitor on exit
        del self.screensaver_monitor
        del self.player_monitor
