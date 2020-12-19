import os


class Encoder:

    @classmethod
    def split_into_tracks(cls, ts_files, duration, debug=False):
        loglevel = "verbose" if debug else "quiet"

        # take out splices from track 0 ts_file and create ts_file1, ts_file2 ..
        for index in range(1, len(ts_files)):
            start_ss = index * duration
            (
                os.system("ffmpeg -y -loglevel {level} -i {input} -c copy  -ss {start} -t {duration} {output}"
                          .format(level=loglevel, input=ts_files[0], start=start_ss, duration=duration,
                                  output=ts_files[index]))
            )

        # trim ts_file 0, so that it contains only track 0 content
        (
            os.system("ffmpeg -y -loglevel {level} -i {input} -c copy -ss {start} -t {duration} {output}"
                      .format(level=loglevel, input=ts_files[0], start=0, duration=duration,
                              output=ts_files[0] + ".ts"))
        )
        os.rename(ts_files[0] + ".ts", ts_files[0])

    @classmethod
    def encode_mkv(cls, ts_files, filepath, duration, debug=False):
        """
        encode to mkv using ffmpeg.
        :param ts_files: list of ts files.
        :param filepath: path of the output mkv file to be created.
        :param duration: duration from the metadata.
        :param debug: debug flag
        :return: True if encode successful.
        """

        # probe size is needed to lookup timestamp info in files where multiple tracks are
        # joined in a single channel and possibly with incorrect timestamps.
        probe_size = 2147483647     # int_max

        # ffmpeg log_level.
        log_level = "verbose" if debug else "quiet"

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
                print("splitting track .. ")
                Encoder.split_into_tracks(ts_files, duration, debug)

            print("encoding output file ..")
            (
                os.system("ffmpeg -y -loglevel {level} {input} -c copy {maps} {output}"
                          .format(level=log_level, input=' '.join(in_args), maps=' '.join(map_args),
                                  output=filepath))
            )
        except Exception as ex:
            print("ffmpeg exception: {}".format(ex))
            print("check the ts file(s) generated at location: {}".format(', '.join(ts_files)))
            return False

        if not debug:
            for ts_file in ts_files:
                os.unlink(ts_file)

        return True

    @classmethod
    def join(cls, files_list, out_dirpath: str, ts_index: int, debug=False):
        """
        join media files into a single ts file.
        :param files_list: list of stream files.
        :param out_dirpath: output directory path.
        :param ts_index: ts file number.
        :param debug: debug flag.
        will be stored.
        :return: return a temporary file combining all the decrypted media files.
        """
        out_filename = "{}.ts".format(ts_index)
        out_filepath = os.path.join(out_dirpath, out_filename)
        with open(out_filepath, 'wb+') as out_fh:
            for file in files_list:
                with open(file, 'rb') as in_fh:
                    out_fh.write(in_fh.read())

                if not debug:
                    os.unlink(file)

        return out_filepath
