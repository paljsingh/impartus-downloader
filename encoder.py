import os
import logging
from shutil import move
from typing import List


class Encoder:
    """
    Utility functions to split, join, encode media streams using ffmpeg.
    """

    @classmethod
    def split_track(cls, ts_files: List, duration: int, debug: bool = False):
        """
        Impartus platform has some m3u8 streams that are badly coded, and put all the stream
        contents to a single track, despite the metadata claiming to have more than 1 tracks.
        In such cases, track 0 contains all the content, while other tracks are 0 sized.
        Split [track 0] into [track 0, track 1, track 2 ..]
        :param ts_files: list of track stream files (presorted by size DESC), so track 0 will always be
        splittable.
        :param duration: Duration of the lecture from the metadata.
        Total size of track 0 is expected to be number_of_tracks * duration
        :param debug: If true, print verbose output of ffmpeg command.
        """
        if debug:
            loglevel = "verbose"
        else:
            loglevel = "quiet"

        # take out splices from track 0 ts_file and create ts_file1, ts_file2 ..
        for index in range(1, len(ts_files)):
            start_ss = index * duration
            (
                os.system("ffmpeg -y -loglevel {level} -i {input} -c copy  -ss {start} -t {duration} {output}"
                          .format(level=loglevel, input=ts_files[0], start=start_ss, duration=duration,
                                  output=ts_files[index]))
            )

        # trim ts_file 0, so that it contains only track 0 content
        tmp_file_path = os.path.join(os.path.dirname(ts_files[0]), "tmp.ts")
        (
            os.system("ffmpeg -y -loglevel {level} -i {input} -c copy -ss {start} -t {duration} {output}"
                      .format(level=loglevel, input=ts_files[0], start=0, duration=duration, output=tmp_file_path))
        )
        # os.rename() fails on windows if the target file exists.
        # using shutils.move
        move(tmp_file_path, ts_files[0])

    @classmethod
    def encode_mkv(cls, ttid, ts_files, filepath, duration, debug=False):
        """
        Encode to mkv using ffmpeg and create a multiview video file.
        :param ts_files: list of track files.
        :param filepath: path of the output mkv file to be created.
        :param duration: duration from the metadata.
        :param debug: debug flag, if True print verbose output from ffmpeg.
        :return: True if encode successful.
        """

        # probe size is needed to lookup timestamp info in files where multiple tracks are
        # joined in a single channel and possibly with incorrect timestamps.
        probe_size = 2147483647     # int_max

        # ffmpeg log_level.
        log_level = "verbose" if debug else "quiet"
        logger = logging.getLogger(cls.__name__)

        try:
            # ffmpeg command syntax we expect to run
            # ffmpeg [global_flags] [in1_flags] -i in1.ts [in2_flags] -i in2.ts .. -c copy -map 0 -map 1 .. $outfile
            in_args = list()
            map_args = list()

            split_flag = False
            for index, ts_file in enumerate(ts_files):
                in_args.append(
                    "-analyzeduration {} -probesize {} -i {}".format(probe_size, probe_size, ts_file))
                map_args.append("-map {}".format(index))

                # if any of the ts_file is 0 sized, it's content exists in track 0
                # split track 0, if that is the case.
                if os.stat(ts_file).st_size == 0:
                    split_flag = True

            if split_flag:
                logger.info("[{}]: splitting track 0 .. ".format(ttid))
                Encoder.split_track(ts_files, duration, debug)

            logger.info("[{}]: encoding output file ..".format(ttid))
            (
                os.system("ffmpeg -y -loglevel {level} {input} -c copy {maps} {output}"
                          .format(level=log_level, input=' '.join(in_args), maps=' '.join(map_args),
                                  output=filepath))
            )
        except Exception as ex:
            logger.error("[{}]: ffmpeg exception: {}".format(ttid, ex))
            logger.error("[{}]: Check the ts file(s) generated at location: {}".format(ttid, ', '.join(ts_files)))
            return False

        return True

    @classmethod
    def join(cls, files_list, out_dirpath: str, track_number: int):
        """
        Join individual stream files into a single track file.
        :param files_list: list of stream files.
        :param out_dirpath: output directory path.
        :param track_number: track number.
        :return: return a track file combining all the decrypted media files.
        """
        out_filename = "track-{}.ts".format(track_number)
        out_filepath = os.path.join(out_dirpath, out_filename)
        with open(out_filepath, 'wb+') as out_fh:
            for file in files_list:
                with open(file, 'rb') as in_fh:
                    out_fh.write(in_fh.read())

        return out_filepath
