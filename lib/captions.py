from datetime import datetime
from typing import List
import html
import os

from lib.config import ConfigType, Config
from lib.threadlogging import ThreadLogger


class Captions:
    """
    Provides utility methods to create a closed captions file in webvtt format.
    It uses the lecture chat data obtained from impartus api to create a captions file, that can be overlay-ed
    as a subtitle/cc window while playing a lecture video.
    """

    thread_logger = ThreadLogger(__name__)

    @classmethod
    def time_vtt_format(cls, value: int):
        sh = value // 3600
        sm = (value % 3600) // 60
        ss = value % 60
        return "{:02d}:{:02d}:{:02d}.000".format(sh, sm, ss)

    @classmethod
    def get_vtt_header(cls, num_msgs=5, window_width_in_pct=10, opacity=0.75,
                       r_anchor_x=0, r_anchor_y=0, v_anchor_x=100, v_anchor_y=25,
                       user_color='#87ceeb', text_color='#dddddd', separator_color='#777777',
                       user_font_size='0.3em', text_font_size='0.35em', separator_font_size='0.25em'):
        return """WEBVTT

REGION
id:chatbox
lines:{num_msgs}
regionanchor:{r_anchor_x}%,{r_anchor_y}%
viewportanchor:{v_anchor_x}%,{v_anchor_y}%
scroll:up
width:{window_width}%

STYLE
::cue-region {{
  background-color: rgba(0,0,0,{opacity});
}}
::cue(v[voice='name'])
{{
  color:{user_color};
  font-size: {user_font_size};
}}
::cue(v[voice='text'])
{{
  font-size:{text_font_size};
  color: {text_color};
}}
::cue(v[voice='line'])
{{
  font-size:{separator_font_size};
  color:{separator_color};
}}
""".format(num_msgs=num_msgs, window_width=window_width_in_pct, opacity=opacity, r_anchor_x=r_anchor_x,
           r_anchor_y=r_anchor_y, v_anchor_x=v_anchor_x, v_anchor_y=v_anchor_y,
           user_color=user_color, text_color=text_color, separator_color=separator_color,
           user_font_size=user_font_size, text_font_size=text_font_size, separator_font_size=separator_font_size)

    @classmethod
    def get_vtt_body(cls, messages: List, start_time_epoch=0):
        vtt = ""

        if not messages:
            return vtt

        first_text_time = messages[0]['time']
        max_duration = 3600  # max duration for a text to stay on screen.

        # negative delay here, chat messages arrive early, impartus api often registers them 5-10 seconds later.
        captions_delay = -10

        # first text arrives 'offset' seconds after the start of lecture.
        offset = first_text_time - start_time_epoch + captions_delay
        if offset < 0:
            offset = 0

        for i in range(len(messages)):
            start_time = messages[i]['time'] - first_text_time + offset
            end_time = start_time + max_duration

            vtt += "{} --> {} region:chatbox align:center text-align:justify\n".format(
                Captions.time_vtt_format(start_time),
                Captions.time_vtt_format(end_time)
            )
            vtt += "<v name>{}\n".format(messages[i]['name'].strip().title())
            vtt += "<v text>{}\n".format(html.unescape(messages[i]['text']).strip())
            vtt += "<v line>. . . . . . . . . . .\n\n"

        return vtt

    @classmethod
    def get_vtt(cls, msgs: List, start_epoch=0):
        conf = Config.load(ConfigType.IMPARTUS)
        r_x, r_y, v_x, v_y = conf.get('chat_window_position').split(',')

        captions_content = Captions.get_vtt_body(msgs, start_epoch)
        if captions_content == "" or captions_content is None:
            raise CaptionsNotFound

        return "{}\n{}".format(
            Captions.get_vtt_header(
                num_msgs=conf.get('chat_window_msgs'),
                window_width_in_pct=conf.get('chat_window_width'),
                opacity=conf.get('chat_window_opacity'),
                r_anchor_x=r_x,
                r_anchor_y=r_y,
                v_anchor_x=v_x,
                v_anchor_y=v_y,
            ),
            captions_content
        )

    @classmethod
    def save_vtt(cls, vtt_content, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w+', encoding="utf-8") as fh:
            fh.write(vtt_content)

    @classmethod
    def save_as_captions(cls, rf_id, video_metadata, chat_msgs, captions_path):
        date_format = "%Y-%m-%d %H:%M:%S"
        start_epoch = int(datetime.strptime(video_metadata['startTime'], date_format).timestamp())
        logger = Captions.thread_logger.logger
        try:
            vtt_content = Captions.get_vtt(chat_msgs, start_epoch)
            Captions.save_vtt(vtt_content, captions_path)
            logger.info("[{}]: Lecture chats saved at {}".format(rf_id, captions_path))
        except CaptionsNotFound:
            logger.error("[{}]: Error saving lecture chats (or no lecture chats found) for {}".format(
                rf_id, captions_path))
            return
        return True


class CaptionsNotFound(Exception):
    pass
