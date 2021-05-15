import logging
import os
import platform
import shutil
import threading
import ast
from functools import partial
from pathlib import Path
from typing import Dict

import tkinter as tk
from tksheet import Sheet
import tkinter.filedialog
import tkinter.messagebox

from lib.config import ConfigType, Config
from lib.impartus import Impartus
from lib.utils import Utils
from ui.data import Columns
from ui.data import Icons
from ui.login_form import LoginForm
from ui.mappings import Mappings
from ui.toolbar import Toolbar
from ui.vars import Variables


class Content:

    def __init__(self, app: tk.Tk, login: LoginForm, toolbar: Toolbar, impartus: Impartus):

        self.app = app
        self.login = login
        self.toolbar = toolbar
        self.impartus = impartus

        conf = Config.load(ConfigType.IMPARTUS)
        self.content_font = conf.get('content_font').get(platform.system())
        self.content_font_size = conf.get('content_font_size')

        self.header_font = conf.get('header_font').get(platform.system())
        self.header_font_size = conf.get('header_font_size')

        self.frame_content = None
        self.sheet = None

        self.videos = None
        self.video_slide_mapping = None

        self.expected_real_paths_differ = False
        self.offline_video_ttid_mapping = None

        # sort options
        self.sort_by = None
        self.sort_order = None

        # threads for downloading videos / slides.
        self.threads = None
        self.dialog = None

    def _init_content(self):
        if self.frame_content:
            self.frame_content.destroy()
        self.frame_content = self.add_content_frame(self.app)

        self.sheet = Sheet(
            self.frame_content,
            header_font=(self.header_font, self.header_font_size, "bold"),
            font=(self.content_font, self.content_font_size, "normal"),
            align='w',
            row_height="1",  # str value for row height in number of lines.
            row_index_align="w",
            auto_resize_default_row_index=False,
            row_index_width=40,
            header_align='center',
            empty_horizontal=0,
            empty_vertical=0,
        )

        self.sheet.enable_bindings((
            "single_select",
            "column_select",
            "column_width_resize",
            "double_click_column_resize",
            "edit_cell",
            "copy",
        ))

        self.sheet.grid(row=0, column=0, sticky='nsew')
        self.set_headers()

        self.set_display_columns()
        self.frame_content.columnconfigure(0, weight=1)
        self.frame_content.rowconfigure(0, weight=1)
        self.sheet.extra_bindings('column_select', self.sort_table)
        self.sheet.extra_bindings('cell_select', self.on_click_button_handler)

        # sort options
        self.sort_by = None
        self.sort_order = None

        # threads for downloading videos / slides.
        self.threads = dict()
        self.dialog = None


    def add_content_frame(self, anchor) -> tk.Frame:    # noqa
        frame_content = tk.Frame(anchor, padx=0, pady=0)
        frame_content.grid(row=2, column=0, sticky='nsew')
        return frame_content

    def set_headers(self, sort_by=None, sort_order=None):
        """
        Set the table headers.
        """
        # set column title to reflect sort status
        headers = list()
        for name, value in Columns.display_columns.items():
            if value.get('sortable'):
                if name == sort_by:
                    sort_icon = Icons.SORT_DESC if sort_order == 'desc' else Icons.SORT_ASC
                else:
                    sort_icon = Icons.UNSORTED
                text = '{} {}'.format(value['display_name'], sort_icon)
            else:
                text = value['display_name']

            if value.get('editable'):
                text = '{} {}'.format(Icons.EDITABLE, text)

            headers.append(text)
        self.sheet.headers(headers)

    def set_display_widgets(self):
        """
        Create the table/sheet.
        Fill in the data for table content, Set the buttons and their states.
        """
        self.fetch_content()
        self.fill_content()

    def on_click_button_handler(self, args):
        """
        On click handler for all the buttons, calls the corresponding function as defined by self.button_columns
        """
        (event, row, col) = args
        real_col = self.get_real_col(col)

        self.sheet.highlight_rows(rows=[row], redraw=False)
        self.sheet.highlight_columns(columns=[col], redraw=False)

        # is subject field
        col_name = Columns.column_names[real_col]
        if Columns.all_columns[col_name].get('editable'):
            old_value = self.sheet.get_cell_data(row, real_col)
            self.sheet.create_text_editor(
                row=row,
                column=real_col,
                text=old_value,
                set_data_ref_on_destroy=False,
                binding=partial(self.end_edit_cell, old_value)
            )

        # not a button.
        if Columns.all_columns[col_name].get('type') != 'button':
            self.sheet.refresh()
            return

        state_button_col_name, state_button_col_num = self.get_state_button(col_name)
        state = self.sheet.get_cell_data(row, state_button_col_num)
        if state == 'False':  # data read from sheet is all string.
            self.sheet.refresh()
            return

        # disable the button if it is one of the Download buttons, to prevent a re-download.
        if col_name == 'download_video':
            self.sheet.set_cell_data(row, real_col, Icons.PAUSE_DOWNLOAD, redraw=False)
        elif col_name == 'download_slides':
            cs = Config.load(ConfigType.COLORSCHEMES)[Variables().colorscheme_var().get()]
            self.disable_button(row, real_col, cs)

        func_name = Columns.all_columns[col_name]['function']
        getattr(self, func_name)(row, real_col)

    def get_state_button(self, button_name):    # noqa
        if Columns.all_columns[button_name].get('state'):
            state_col_name = Columns.all_columns[button_name].get('state')
            state_col_number = Columns.column_names.index(state_col_name)
            return state_col_name, state_col_number
        else:
            return None, None

    def end_edit_cell(self, old_value, event=None):
        row, col = (event[0], event[1])
        new_value = self.sheet.get_text_editor_value(
            event,
            r=row,
            c=col,
            set_data_ref_on_destroy=True,
            move_down=True,
            redraw=True,
            recreate=True
        )

        # empty value or escape pressed.
        if not new_value or new_value == '':
            return

        # no changes made.
        if old_value == new_value:
            return

        self.expected_real_paths_differ = True
        self.toolbar.auto_organize_button.config(state='normal')
        col_name = Columns.column_names[self.get_real_col(col)]
        columns_item = Columns.data_columns[col_name]
        orig_values_col_name = columns_item.get('original_values_col')
        original_value = self.sheet.get_cell_data(row, Columns.column_names.index(orig_values_col_name))
        for i, data in enumerate(self.sheet.get_column_data(Columns.column_names.index(orig_values_col_name))):
            if data == original_value:
                self.sheet.set_cell_data(i, col, new_value)

        Mappings.update_mappings(orig_values_col_name, original_value, new_value)

        self.reset_column_sizes()
        self.sheet.refresh()

    def reset_column_sizes(self):
        """
        Adjust column sizes after data has been filled.
        """
        # resize cells
        self.sheet.set_all_column_widths()

        # reset column widths to fill the screen
        pad = 5
        column_widths = self.sheet.get_column_widths()
        table_width = self.sheet.RI.current_width + sum(column_widths) + len(column_widths) + pad
        diff_width = self.frame_content.winfo_width() - table_width

        # adjust extra width only to top N data columns
        n = 3
        column_states = [v.get() for v in Variables().display_columns_vars().values()]
        count = 0
        for k, v in enumerate(column_states):
            if Columns.column_names[k] == 'downloaded':
                break
            count += v
        # range(0..count) is all data columns.
        data_col_widths = {k: v for k, v in enumerate(column_widths[:count])}
        top_n_cols = sorted(data_col_widths, key=data_col_widths.get, reverse=True)[:n]
        for i in top_n_cols:
            self.sheet.column_width(i, column_widths[i] + diff_width // n)

    def get_index(self, row):
        """
        Find the values stored in the hidden column named 'Index', given a row record.
        In case the row value has been updated due to sorting the table, Index field helps identify the new location
        of the associated record.
        """
        # find where is the Index column
        index_col = Columns.column_names.index('index')
        # original row value as per the index column
        return int(self.sheet.get_cell_data(row, index_col))

    def get_row_after_sort(self, index_value):
        # find the new correct location of the row_index
        col_index = Columns.column_names.index('index')
        col_data = self.sheet.get_column_data(col_index)
        return col_data.index(str(index_value))

    def progress_bar_text(self, value, processed=False):
        """
        return progress bar text, calls the unicode/ascii implementation.
        """
        conf = Config.load(ConfigType.IMPARTUS)
        if conf.get('progress_bar') == 'unicode':
            text = self.progress_bar_text_unicode(value)
        else:
            text = self.progress_bar_text_ascii(value)

        pad = ' ' * 2
        if 0 < value < 100:
            percent_text = '{:2d}%'.format(value)
            status = percent_text
        elif value == 0:
            status = '{}{}{}'.format(pad, Icons.VIDEO_NOT_DOWNLOADED, pad)
        else:  # 100 %
            if processed:
                status = '{}{}{}'.format(pad, Icons.VIDEO_DOWNLOADED, pad)
            else:
                status = '{}{}{}'.format(pad, Icons.VIDEO_PROCESSING, pad)
        return '{} {}{}'.format(text, status, pad)

    def progress_bar_text_ascii(self, value):  # noqa
        """
        progress bar implementation with ascii characters.
        """
        bars = 50
        ascii_space = " "
        if value > 0:
            progress_text = '{}'.format('❘' * (value * bars // 100))
            empty_text = '{}'.format(ascii_space * (bars - len(progress_text)))
            full_text = '{}{} '.format(progress_text, empty_text)
        else:
            full_text = '{}'.format(ascii_space * bars)

        return full_text

    def progress_bar_text_unicode(self, value):  # noqa
        """
        progress bar implementation with unicode blocks.
        """
        chars = ['▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']

        # 1 full unicode block = 8 percent values
        # => 13 unicode blocks needed to represent counter 100.
        unicode_space = ' '
        if value > 0:
            # progress_text: n characters, empty_text: 13-n characters
            progress_text = '{}{}'.format(chars[-1] * (value // 8), chars[value % 8])
            empty_text = '{}'.format(unicode_space * (13 - len(progress_text)))
            full_text = '{}{}'.format(progress_text, empty_text)
        else:
            # all 13 unicode whitespace.
            full_text = '{} '.format(unicode_space * 13)
        return full_text

    def progress_bar_callback(self, count, row, col, processed=False):
        """
        Callback function passed to the backend, where it computes the download progress.
        Every time the function is called, it will update the progress bar value.
        """
        updated_row = self.get_row_after_sort(row)
        new_text = self.progress_bar_text(count, processed)
        if new_text != self.sheet.get_cell_data(updated_row, col):
            self.sheet.set_cell_data(updated_row, col, new_text, redraw=True)

    def get_real_col(self, col):    # noqa
        """
        with configurable column list, the col number returned by tksheet may not be the same as
        column no from self.all_columns/self.display_columns. Use self.display_column_vars to identify and return
        the correct column.
        """
        # find n-th visible column, where n=col
        i = 0
        for c, state in enumerate(Variables().display_columns_vars().values()):
            if state.get() == 1:
                if i == col:
                    return c
                i += 1

    def fetch_content(self):
        self.videos = dict()
        self.video_slide_mapping = dict()
        self.expected_real_paths_differ = False
        self.offline_video_ttid_mapping = None

        root_url = self.login.url_box.get()
        subject_dicts = self.impartus.get_subjects(root_url)
        has_flipped_lectures = False
        for subject_dict in subject_dicts:
            videos_by_subject = self.impartus.get_lectures(root_url, subject_dict)
            flipped_videos_by_subject = self.impartus.get_flipped_lectures(root_url, subject_dict)
            if len(flipped_videos_by_subject):
                has_flipped_lectures = True
            all_videos_by_subject = [*videos_by_subject, *flipped_videos_by_subject]
            slides = self.impartus.get_slides(root_url, subject_dict)
            mapping_dict = self.impartus.map_slides_to_videos(all_videos_by_subject, slides)
            for key, val in mapping_dict.items():
                self.video_slide_mapping[key] = val
            self.videos[subject_dict.get('subjectId')] = {x['ttid']: x for x in all_videos_by_subject}

        self.toolbar.update(flipped=has_flipped_lectures)

    def fill_content(self):
        # A mapping dict containing previously downloaded, and possibly moved around / renamed videos.
        # extract their ttid and map those to the correct records, to avoid forcing the user to re-download.
        self.offline_video_ttid_mapping = self.impartus.get_mkv_ttid_map()

        row = 0
        sheet_rows = list()
        for subject_id, videos in self.videos.items():
            for ttid, video_metadata in videos.items():
                video_metadata = Utils.add_new_fields(video_metadata, self.video_slide_mapping)

                video_path = self.impartus.get_mkv_path(video_metadata)
                if not os.path.exists(video_path):
                    # or search from the downloaded videos, using video_ttid_map
                    video_path_moved = self.offline_video_ttid_mapping.get(str(ttid))

                    if video_path_moved:
                        # For now, use the offline path if a video found. Also set the flag to enable move/rename button
                        video_path = video_path_moved
                        self.expected_real_paths_differ = True

                slides_path = self.impartus.get_slides_path(video_metadata)

                video_exists_on_disk = video_path and os.path.exists(video_path)
                slides_exist_on_server = self.video_slide_mapping.get(ttid)
                slides_exist_on_disk, slides_path = self.impartus.slides_exist_on_disk(slides_path)

                metadata = {
                    'video_metadata': video_metadata,
                    'video_path': video_path,
                    'video_exists_on_disk': video_exists_on_disk,
                    'slides_exist_on_server': slides_exist_on_server,
                    'slides_exist_on_disk': slides_exist_on_disk,
                    'slides_url': self.video_slide_mapping.get(ttid),
                    'slides_path': slides_path,
                }
                row_items = list()
                button_states = list()

                # data items
                for col, (key, item) in enumerate(Columns.all_columns.items()):
                    text = ''
                    if item['type'] == 'data':
                        text = video_metadata[key]
                        # title case
                        if item.get('title_case'):
                            text = " ".join(text.splitlines()).strip().title()
                    elif item['type'] == 'auto':
                        text = row
                    elif item['type'] == 'progressbar':
                        if video_exists_on_disk:
                            text = self.progress_bar_text(100, processed=True)
                        else:
                            text = self.progress_bar_text(0)
                    elif item['type'] == 'button':
                        button_states.append(self.get_button_state(
                            key, video_exists_on_disk, slides_exist_on_server, slides_exist_on_disk)
                        )
                        text = item.get('text')
                    elif item['type'] == 'button_state':
                        text = button_states.pop(0)
                    elif item['type'] == 'metadata':
                        text = metadata
                    elif item['type'] == 'original_value':
                        text = video_metadata[key]
                    row_items.append(text)

                row += 1
                sheet_rows.append(row_items)

        self._init_content()
        self.sheet.insert_rows(sheet_rows, idx='end')

        self.reset_column_sizes()
        self.decorate()

        # update button status
        self.set_button_status(redraw=True)
        self.sheet.grid(row=0, column=0, sticky='nsew')

    def sort_table(self, args):
        """
        Sorts the table content.
        """
        col = args[1]
        real_col = self.get_real_col(col)
        self.sheet.deselect("all")

        col_name = Columns.column_names[real_col]
        if not Columns.all_columns[col_name].get('sortable'):
            return

        sort_by = col_name
        if sort_by == self.sort_by:
            sort_order = 'asc' if self.sort_order == 'desc' else 'desc'
        else:
            sort_order = 'desc'
        self.sort_by = sort_by
        self.sort_order = sort_order

        reverse = True if sort_order == 'desc' else False

        table_data = self.sheet.get_sheet_data()
        table_data.sort(key=lambda x: x[real_col], reverse=reverse)

        self.set_headers(sort_by, sort_order)
        self.set_button_status()
        self.sheet.refresh()

    def _download_video(self, video_metadata, filepath, root_url, row, col, pause_ev, resume_ev):  # noqa
        """
        Download a video in a thread. Update the UI upon completion.
        """
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        pb_col = Columns.column_names.index('downloaded')

        # # voodoo alert:
        # It is possible for user to sort the table while download is in progress.
        # In such a case, the row index supplied to the function call won't match the row index
        # required to update the correct progressbar/open/play buttons, which now exists at a new
        # location.
        # The hidden column index keeps the initial row index, and remains unchanged.
        # Use row_index to identify the new correct location of the progress bar.
        row_index = self.get_index(row)

        imp.process_video(video_metadata, filepath, root_url, pause_ev, resume_ev,
                          partial(self.progress_bar_callback, row=row_index, col=pb_col),
                          video_quality=Variables().lecture_quality_var())

        # download complete, enable open / play buttons
        updated_row = self.get_row_after_sort(row_index)
        # update progress bar status to complete.
        self.progress_bar_callback(row=row_index, col=pb_col, count=100, processed=True)

        self.sheet.set_cell_data(updated_row, Columns.column_names.index('download_video'), Icons.DOWNLOAD_VIDEO)

        self.disable_button(updated_row, Columns.column_names.index('download_video'))
        # enable buttons.
        self.enable_button(updated_row, Columns.column_names.index('open_folder'))
        self.enable_button(updated_row, Columns.column_names.index('play_video'))

    def add_slides(self, row, col):  # noqa
        conf = Config.load(ConfigType.IMPARTUS)
        file_types = [(str(ext).upper(), '*.{}'.format(ext)) for ext in conf.get('allowed_ext')]
        filepaths = tkinter.filedialog.askopenfilenames(filetypes=file_types)

        data = self.read_metadata(row)
        slides_folder_path = os.path.dirname(data.get('video_path'))

        for filepath in filepaths:
            shutil.copy(filepath, slides_folder_path)

    def pause_resume_button_click(self, row, col, pause_event, resume_event):
        row_index = self.get_index(row)
        updated_row = self.get_row_after_sort(row_index)

        if pause_event.is_set():
            self.sheet.set_cell_data(updated_row, col, Icons.PAUSE_DOWNLOAD, redraw=True)
            resume_event.set()
            pause_event.clear()
        else:
            self.sheet.set_cell_data(updated_row, col, Icons.RESUME_DOWNLOAD, redraw=True)
            pause_event.set()
            resume_event.clear()

    def download_video(self, row, col):
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        data = self.read_metadata(row)

        video_metadata = data.get('video_metadata')
        filepath = data.get('video_path')
        root_url = self.login.url_box.get()

        real_row = self.get_index(row)

        if self.threads.get(real_row):
            pause_ev = self.threads.get(real_row)['pause_event']
            resume_ev = self.threads.get(real_row)['resume_event']
            self.pause_resume_button_click(row, col, pause_ev, resume_ev)
            return

        from threading import Event

        pause_event = Event()
        resume_event = Event()

        # note: args is a tuple.
        thread = threading.Thread(target=self._download_video, args=(video_metadata, filepath, root_url, row, col,
                                                                     pause_event, resume_event,))
        self.threads[real_row] = {
            'thread': thread,
            'pause_event': pause_event,
            'resume_event': resume_event,
        }
        thread.start()

    def _download_slides(self, ttid, file_url, filepath, root_url, row):
        """
        Download a slide doc in a thread. Update the UI upon completion.
        """
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        if imp.download_slides(ttid, file_url, filepath, root_url):
            # download complete, enable show slides buttons
            self.enable_button(row, Columns.column_names.index('show_slides'))
        else:
            tkinter.messagebox.showerror('Error', 'Error downloading slides, see console logs for details.')
            self.enable_button(row, Columns.column_names.index('download_slides'))

    def download_slides(self, row, col):  # noqa
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        data = self.read_metadata(row)

        video_metadata = data.get('video_metadata')
        ttid = video_metadata['ttid']
        file_url = data.get('slides_url')
        filepath = data.get('slides_path')
        root_url = self.login.url_box.get()

        # note: args is a tuple.
        thread = threading.Thread(target=self._download_slides,
                                  args=(ttid, file_url, filepath, root_url, row,))
        # self.threads.append(thread)
        thread.start()

    def read_metadata(self, row):
        """
        We saved a hidden column 'metadata' containing metadata for each record.
        Extract it, and eval it as python dict.
        """
        metadata_col = Columns.column_names.index('metadata')
        data = self.sheet.get_cell_data(row, metadata_col)
        return ast.literal_eval(data)

    def open_folder(self, row, col):  # noqa
        """
        fetch video_path's folder from metadata column's cell and open system launcher with it.
        """
        data = self.read_metadata(row)
        video_folder_path = os.path.dirname(data.get('video_path'))
        Utils.open_file(video_folder_path)

    def play_video(self, row, col):  # noqa
        """
        fetch video_path from metadata column's cell and open system launcher with it.
        """
        data = self.read_metadata(row)
        Utils.open_file(data.get('video_path'))

    def show_slides(self, row, col):  # noqa
        """
        fetch slides_path from metadata column's cell and open system launcher with it.
        """
        data = self.read_metadata(row)
        Utils.open_file(data.get('slides_path'))

    def auto_organize(self):
        self.toolbar.auto_organize_button.config(state='disabled')

        logger = logging.getLogger(self.__class__.__name__)
        moved_files = dict()

        conf = Config.load(ConfigType.IMPARTUS)
        for subject_id, videos in self.videos.items():
            for ttid, video_metadata in videos.items():
                video_metadata = Utils.add_new_fields(video_metadata, self.video_slide_mapping)
                # for videos
                expected_video_path = self.impartus.get_mkv_path(video_metadata)
                real_video_path = self.offline_video_ttid_mapping.get(str(ttid))

                if real_video_path and expected_video_path != real_video_path and os.path.exists(real_video_path):
                    Utils.move_and_rename_file(real_video_path, expected_video_path)
                    logger.info('moved {} -> {}'.format(real_video_path, expected_video_path))
                    moved_files[real_video_path] = expected_video_path

                    # also check any slides.
                    for ext in conf.get('allowed_ext'):
                        slides_path = '{}.{}'.format(real_video_path[:-len(".mkv")], ext)
                        if os.path.exists(slides_path):
                            expected_slides_path = '{}.{}'.format(expected_video_path[:-len(".mkv")], ext)
                            Utils.move_and_rename_file(slides_path, expected_slides_path)
                            logger.info('moved {} -> {}'.format(slides_path, expected_slides_path))
                            moved_files[slides_path] = expected_slides_path

                    # is the folder empty, remove it.? [also any empty parent folders]
                    old_video_dir = os.path.dirname(real_video_path)
                    sys_name = platform.system()
                    if conf.get('ignore_files').get(sys_name):
                        ignore_files = conf.get('ignore_files')[sys_name]
                    else:
                        ignore_files = []
                    while True:
                        dir_files = [x for x in os.listdir(old_video_dir) if x not in ignore_files]
                        if len(dir_files) > 0:
                            break
                        for file in ignore_files:
                            filepath = os.path.join(old_video_dir, file)
                            if os.path.exists(filepath):
                                os.unlink(filepath)
                        os.rmdir(old_video_dir)
                        logger.info('removed empty directory: {}'.format(old_video_dir))
                        # parent path.
                        old_video_dir = Path(old_video_dir).parent.absolute()

        # show a dialog with the output.
        self.move_file_info_dialog(moved_files)
        self.expected_real_paths_differ = False

    def move_file_info_dialog(self, moved_files):
        # only 1 dialog at a time.
        if self.dialog:
            return

        if len(moved_files) == 0:
            return

        dialog = tk.Toplevel()
        dialog.protocol("WM_DELETE_WINDOW", self.on_move_file_dialog_close)
        dialog.geometry("1000x500+100+100")
        dialog.title('Alert - file rename!')
        dialog.grab_set()

        title = tk.Label(dialog, text='Following files were moved / renamed -', )
        title.grid(row=0, column=0, sticky='w', ipadx=10, ipady=10)

        sheet = Sheet(
            dialog,
            header_font=(self.header_font, self.header_font_size, "bold"),
            font=(self.content_font, self.content_font_size, "normal"),
            align='w',
            row_height="1",  # str value for row height in number of lines.
            row_index_align="w",
            auto_resize_default_row_index=False,
            row_index_width=40,
            header_align='center',
            empty_horizontal=0,
            empty_vertical=0,
        )

        sheet.headers(['Source', '', 'Destination'])
        target_parent = os.path.dirname(self.impartus.download_dir)
        for row, (source, destination) in enumerate(moved_files.items()):
            source = source[len(target_parent) + 1:]
            destination = destination[len(target_parent) + 1:]
            sheet.insert_row([source, Icons.MOVED_TO, destination])
            dialog.columnconfigure(0, weight=1)

        sheet.set_all_column_widths()
        sheet.grid(row=1, column=0, sticky='nsew')

        ok_button = tk.Button(dialog, text='OK', command=self.on_move_file_dialog_close)
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        self.dialog = dialog

    def on_move_file_dialog_close(self):
        self.dialog.destroy()
        self.dialog = None
        self.login.authenticate(self.impartus)

    def set_display_columns(self):
        column_states = [i for i, v in enumerate(Variables().display_columns_vars().values()) if v.get() == 1]
        self.sheet.display_columns(indexes=column_states, enable=True, redraw=False)
        self.reset_column_sizes()
        self.sheet.refresh()

    def odd_even_color(self, cs: Dict, redraw=False):
        """
        Apply odd/even colors for table for better looking UI.
        """
        num_rows = self.sheet.total_rows()

        self.sheet.highlight_rows(
            list(range(0, num_rows, 2)),
            bg=cs['even_row']['bg'],
            fg=cs['even_row']['fg'],
            redraw=redraw
        )
        self.sheet.highlight_rows(
            list(range(1, num_rows, 2)),
            bg=cs['odd_row']['bg'],
            fg=cs['odd_row']['fg'],
            redraw=redraw
        )

    def progress_bar_color(self, cs: Dict, redraw=True):
        """
        Set progress bar color.
        """
        col = Columns.column_names.index('downloaded')
        num_rows = self.sheet.total_rows()

        for row in range(num_rows):
            odd_even_bg = cs['odd_row']['bg'] if row % 2 else cs['even_row']['bg']
            self.sheet.highlight_cells(
                row, col, fg=cs['progressbar']['fg'], bg=odd_even_bg, redraw=redraw)

    def set_button_status(self, redraw=False):
        """
        reads the states of the buttons from the hidden state columns, and sets the button states appropriately.
        """
        col_indexes = [x for x, v in enumerate(Columns.all_columns.values()) if v['type'] == 'button_state']
        num_buttons = len(col_indexes)
        for row, row_item in enumerate(self.sheet.get_sheet_data()):
            for col in col_indexes:
                # data set via sheet.insert_row retains tuple/list's element data type,
                # data set via sheet.set_cell_data makes everything a string.
                # Consider everything coming out of a sheet as string to avoid any issues.
                state = str(row_item[col])

                if state == 'True':
                    self.enable_button(row, col - num_buttons, redraw=redraw)
                elif state == 'False':
                    self.disable_button(row, col - num_buttons, redraw=redraw)
        return

    def get_button_state(self, key, video_exists_on_disk, slides_exist_on_server, slides_exist_on_disk):  # noqa
        """
        Checks to identify when certain buttons should be enabled/disabled.
        """
        state = True
        if key == 'download_video' and video_exists_on_disk:
            state = False
        elif key == 'open_folder' and not video_exists_on_disk:
            state = False
        elif key == 'play_video' and not video_exists_on_disk:
            state = False
        elif key == 'download_slides' and (slides_exist_on_disk or not slides_exist_on_server):
            state = False
        elif key == 'show_slides' and not slides_exist_on_disk:
            state = False
        return state

    def disable_button(self, row, col, redraw=False):
        """
        Disable a button given it's row/col position.
        """
        cs = Config.load(ConfigType.COLORSCHEMES)[Variables().colorscheme_var().get()]

        self.sheet.highlight_cells(
            row, col, bg=cs['disabled']['bg'],
            fg=cs['disabled']['fg'],
            redraw=redraw
        )

        # update state field.
        state_button_col_name, state_button_col_num = self.get_state_button(Columns.column_names[col])
        self.sheet.set_cell_data(row, state_button_col_num, False, redraw=redraw)

    def enable_button(self, row, col, redraw=False):
        """
        Enable a button given it's row/col position.
        """
        cs = Config.load(ConfigType.COLORSCHEMES)[Variables().colorscheme_var().get()]

        odd_even_bg = cs['odd_row']['bg'] if row % 2 else cs['even_row']['bg']
        odd_even_fg = cs['odd_row']['fg'] if row % 2 else cs['even_row']['fg']
        self.sheet.highlight_cells(row, col, bg=odd_even_bg, fg=odd_even_fg, redraw=redraw)

        # update state field.
        state_button_col_name, state_button_col_num = self.get_state_button(Columns.column_names[col])
        self.sheet.set_cell_data(row, state_button_col_num, True, redraw=redraw)

    def set_readonly_columns(self, redraw=False):
        readonly_cols = [i for i, (k, v) in enumerate(Columns.all_columns.items()) if not v.get('editable')]
        self.sheet.readonly_columns(columns=readonly_cols, readonly=True, redraw=redraw)

    def set_colorscheme(self, cs):
        if self.frame_content:
            self.frame_content.configure(bg=cs['root']['bg'])
        if self.sheet:
            self.sheet.set_options(
                frame_bg=cs['table']['bg'],
                table_bg=cs['table']['bg'],
                table_fg=cs['table']['fg'],
                header_bg=cs['header']['bg'],
                header_fg=cs['header']['fg'],
                header_grid_fg=cs['table']['grid'],
                index_grid_fg=cs['table']['grid'],
                header_border_fg=cs['table']['grid'],
                index_border_fg=cs['table']['grid'],
                table_grid_fg=cs['table']['grid'],
                top_left_bg=cs['header']['bg'],
                top_left_fg=cs['header']['bg']
            )
            self.odd_even_color(cs, redraw=False)
            self.progress_bar_color(cs, redraw=False)
            self.set_button_status(redraw=False)
            self.set_readonly_columns(redraw=False)
            self.sheet.refresh()

    def decorate(self):
        """
        calls multiple ui related tweaks.
        """
        self.align_columns()
        cs = Config.load(ConfigType.COLORSCHEMES)[Variables().colorscheme_var().get()]
        self.set_colorscheme(cs)
        self.odd_even_color(cs)
        self.progress_bar_color(cs)

    def align_columns(self):
        # data and progressbar west/left aligned, button center aligned.
        self.sheet.align_columns([Columns.column_names.index(k) for k in Columns.data_columns.keys()], align='w')
        self.sheet.align_columns([Columns.column_names.index(k) for k in Columns.progressbar_column.keys()], align='w')
        self.sheet.align_columns([Columns.column_names.index(k) for k in Columns.button_columns.keys()], align='center')

    def show_video_callback(self, impartus: Impartus):
        self.toolbar.reload_button.config(state='disabled')
        self.toolbar.auto_organize_button.config(state='disabled')
        self.toolbar.frame_toolbar.grid(row=1, column=0, sticky='ew')

        self.login.authenticate(impartus)
        self.set_display_widgets()
        self.toolbar.reload_button.config(state='normal')
        self.toolbar.auto_organize_button.config(state='normal')
