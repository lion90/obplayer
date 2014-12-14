#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2012-2015 OpenBroadcaster, Inc.

This file is part of OpenBroadcaster Player.

OpenBroadcaster Player is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenBroadcaster Player is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with OpenBroadcaster Player.  If not, see <http://www.gnu.org/licenses/>.
"""

import obplayer

import os
import magic
import time
import random

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GstPbutils


class ObFallbackPlayer (obplayer.ObPlayerController):

    def __init__(self):
        self.media = []

        self.media_types = []
        self.image_types = []

        self.media_types.append('audio/x-flac')
        self.media_types.append('audio/flac')
        self.media_types.append('audio/mpeg')
        self.media_types.append('audio/ogg')

        # TODO we're always headless new so we never play images or video??
        #if obplayer.Config.headless == False:
        self.image_types.append('image/jpeg')
        self.image_types.append('image/png')
        self.image_types.append('image/svg+xml')
        self.media_types.append('application/ogg')
        self.media_types.append('video/ogg')
        self.media_types.append('video/x-msvideo')
        self.media_types.append('video/mp4')
        self.media_types.append('video/mpeg')

        self.play_index = 0
        self.image_duration = 15.0

        m = magic.open(magic.MAGIC_MIME)
        m.load()

        for (dirname, dirnames, filenames) in os.walk(obplayer.Config.setting('fallback_media')):
            for filename in filenames:
                filetype = m.file(os.path.join(dirname, filename)).split(';')[0]

                if filetype in self.media_types:
		    d = GstPbutils.Discoverer()
		    mediainfo = d.discover_uri("file://" + obplayer.Config.setting('fallback_media') + '/' + filename)

		    media_type = None
		    for stream in mediainfo.get_video_streams():
			if stream.is_image():
			    media_type = 'image'
			else:
			    media_type = 'video'
			    break
		    if not media_type and len(mediainfo.get_audio_streams()) > 0:
			media_type = 'audio'

		    if media_type:
			# we discovered some more fallback media, add to our media list.
			self.media.append([filename, media_type, mediainfo.get_duration() / Gst.SECOND])

                if filetype in self.image_types:
                    self.media.append([filename, 'image', self.image_duration])

        # shuffle the list
        random.shuffle(self.media)

	self.ctrl = obplayer.Player.create_controller('fallback', 25)
	self.ctrl.set_request_callback(self.do_player_request)

    # the player is asking us what to play next
    def do_player_request(self, ctrl, present_time):

	"""
        # early return if we're playing something already, have no fallback media, or scheduler is about to do something.
        if obplayer.Player.is_playing() or len(self.media) == 0 or obplayer.Scheduler.next_update() - time.time() < 5:
            return True
	"""

        if len(self.media) <= self.play_index:
            self.play_index = 0
            random.shuffle(self.media)  # shuffle again to create a new order for next time.

	"""
        # nothing playing? well let's play something.
        media = {
	    'media_id': 0,
	    'order_num': 0,
	    'media_type': unicode(self.media[self.play_index][1]),
	    'file_location': unicode(obplayer.Config.setting('fallback_media')),
	    'filename': unicode(self.media[self.play_index][0]),
	    'artist': u'unknown',
	    'title': unicode(self.media[self.play_index][0]),
	    'start_time': 0.0,
	    'duration': self.media[self.play_index][2]
	}

        obplayer.Player.play(media, 0, 'fallback')
	"""

	print "Requesting player play " + self.media[self.play_index][0] + " for " + str(self.media[self.play_index][2]) + "s (" + self.media[self.play_index][1] + ")"
	ctrl.add_request(
	    media_type = unicode(self.media[self.play_index][1]),
	    file_location = unicode(obplayer.Config.setting('fallback_media')),
	    filename = unicode(self.media[self.play_index][0]),
	    duration = self.media[self.play_index][2],
	    order_num = self.play_index,
	    artist = u'unknown',
	    title = unicode(self.media[self.play_index][0])
	)

        self.play_index = self.play_index + 1

        return True


