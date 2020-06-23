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
        self.active = False
        self.changed = False

    def onScreensaverActivated(self):
        utils.log("screen saver on", xbmc.LOGDEBUG)
        self.active = True
        self.changed = True

    def onScreensaverDeactivated(self):
        utils.log("screen saver off", xbmc.LOGDEBUG)
        self.active = False
        self.changed = True

class PlayerMonitor(xbmc.Player):

    def __init__(self):
        xbmc.Player.__init__(self)
        self.content = "MOVIE"
        self.state = "STOP"
        self.changed = False
  
    def onPlayBackStarted(self):
        utils.log("play", xbmc.LOGDEBUG)
        if self.isPlayingVideo():
            self.content = "MOVIE"
            utils.log(self.content)
        else:
            self.content = "MUSIC"
            utils.log(self.content)
        self.state = "PLAY"
        self.changed = True

    def onPlayBackStopped(self):
        utils.log("stop", xbmc.LOGDEBUG)
        self.state = "STOP"
        self.changed = True

    def onPlayBackPaused(self):
        utils.log("pause", xbmc.LOGDEBUG)
        self.state = "PAUSE"
        self.changed = True

    def onPlayBackResume(self):
        utils.log("resume", xbmc.LOGDEBUG)
        self.state = "PLAY"
        self.changed = True

    def onPlayBackEnded(self):
        utils.log("end", xbmc.LOGDEBUG)
        self.state = "STOP"
        self.changed = True

class AmbilightController():
    screensaver_monitor = None
    player_monitor = None
    addon = xbmcaddon.Addon(ADDON_ID)

    def __init__(self):
        self.player_monitor = PlayerMonitor()
        self.screensaver_monitor = ScreensaverMonitor()


    def runProgram(self):      
        while not xbmc.abortRequested:
            if (self.player_monitor.changed or self.screensaver_monitor.changed):
                self.player_monitor.changed = False
                self.screensaver_monitor.changed = False
                self.ambilight_update()
            xbmc.sleep(500)

        #clean up monitor on exit
        del self.screensaver_monitor
        del self.player_monitor

    def ambilight_update(self):
       
        ambilight_screensaver_setting = self.addon.getSetting('ambilight_screensaver')

        if self.player_monitor.state == "PLAY":
            self.ambilight_switch(True)
        elif self.player_monitor.state == "PAUSE" and not self.screensaver_monitor.active and ambilight_screensaver_setting == "True":
            self.ambilight_switch(True)
        else:
            self.ambilight_switch(False)

    def ambilight_switch(self, state):

        ambilight_movie_mode = self.addon.getSetting('ambilight_movie_mode')
        ambilight_music_mode = self.addon.getSetting('ambilight_music_mode')
        ambilight_music = self.addon.getSetting('ambilight_music')


        config = {}
        config["api_version"] = self.addon.getSetting('api_version')
        config['user'] = self.addon.getSetting('user')
        config['pass'] = self.addon.getSetting('pass')
        config['address'] = self.addon.getSetting('tv_ipaddress')
        config['api_port'] = self.addon.getSetting('api_port')
        config['api_protocol'] = self.addon.getSetting('api_protocol')
        config['auth'] = HTTPDigestAuth(config['user'], config['pass'])

        if state:
            if self.player_monitor.content == "MOVIE":
                config['path'] = available_commands_post["ambilight_video_"+ambilight_movie_mode]['path']
                config['body'] = available_commands_post["ambilight_video_"+ambilight_movie_mode]['body']
                pylips.post(config)
                utils.log(self.player_monitor.content + " ambilight ON")

            if ambilight_music == "True" and self.player_monitor.content == "MUSIC":
                config['path'] = available_commands_post["ambilight_audio_"+ambilight_music_mode]['path']
                config['body'] = available_commands_post["ambilight_audio_"+ambilight_music_mode]['body']
                pylips.post(config)
                utils.log(self.player_monitor.content + " ambilight ON")
        else:
            config['path'] = available_commands_post["ambilight_off"]['path']
            config['body'] = available_commands_post["ambilight_off"]['body']
            pylips.post(config)
            utils.log("ambilight OFF")
