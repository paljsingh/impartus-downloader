#!/usr/bin/env python3

import argparse
import base64
import json
import os
import re
import sys
from functools import partial
from typing import List

from lib.captions import Captions
from lib.core.impartus import Impartus
from lib.utils import Utils
from lib.variables import Variables


def validate_numeric(id_value):
    if re.match(r'[0-9]+', str(id_value)):
        return id_value
    raise argparse.ArgumentTypeError("Bad numeric value {}".format(id_value))


def validate_email(user_email: str):
    if '@' in user_email:
        return user_email
    raise argparse.ArgumentTypeError("Bad user/email {}".format(user_email))


def validate_jwt_token(jwt_token: str):
    token_parts = '.'.split(jwt_token)
    if len(token_parts) != 3:
        raise argparse.ArgumentTypeError("Bad jwt token {}".format(token))
    if base64.b64decode(token_parts[0]) and base64.b64decode(token_parts[1]):
        return token
    raise argparse.ArgumentTypeError("jwt token cannot be decoded.")


def error(message):
    print('ERROR: {}'.format(message))


def login():
    if impartus.login():
        print(impartus.token)
    else:
        error("Unable to authenticate.")


def subjects():
    subject_list = impartus.get_subjects()
    if vars(app_args).get('dir'):
        os.makedirs(app_args.dir, exist_ok=True)
        for subject_data in subject_list:
            filename = re.sub(r'[^a-zA-Z0-9._-]+', '', subject_data.get('subjectName'))
            with open('{}/{}.json'.format(app_args.dir, filename), 'w') as fh:
                json.dump(subject_data, fh, indent=4)
    else:
        print(json.dumps(subject_list, indent=4))


def lectures():
    with open(app_args.json, 'r') as fh:
        subject_json = json.load(fh)
    videos_list = impartus.get_lecture_videos([subject_json])
    if vars(app_args).get('dir'):
        os.makedirs(app_args.dir, exist_ok=True)
        for video_metadata in videos_list:
            filename = os.path.basename(Utils.get_mkv_path(video_metadata[1]))
            with open('{}/{}.json'.format(app_args.dir, filename), 'w') as fh:
                json.dump(video_metadata[1], fh, indent=4)
    else:
        print(json.dumps([x[1] for x in videos_list], indent=4))


def documents():
    with open(app_args.json, 'r') as fh:
        subject_json = json.load(fh)
    _, docs_list = next(impartus.get_slides([subject_json]))
    if vars(app_args).get('dir'):
        os.makedirs(app_args.dir, exist_ok=True)
        for i, doc_metadata in enumerate(docs_list):
            filename = '{:02d}-{}'.format(i, os.path.basename(doc_metadata.get('filePath')))
            with open('{}/{}.json'.format(app_args.dir, filename), 'w') as fh:
                json.dump(doc_metadata, fh, indent=4)
    else:
        print(json.dumps(docs_list, indent=4))


def progress_log(value: int):
    if value % 10 == 0:
        print("^", end='')
    else:
        print(".", end='')
    if value == 100:
        print("\n")
    sys.stdout.flush()


def download_video():
    with open(app_args.json, 'r') as fh:
        video_metadata = json.load(fh)
    callback = partial(progress_log)
    mkv_filepath = '{}/{}'.format(app_args.dir, os.path.basename(Utils.get_mkv_path(video_metadata)))
    impartus.process_video(video_metadata, mkv_filepath, None, None, callback, app_args.quality)


def download_chat():
    with open(app_args.json, 'r') as fh:
        video_metadata = json.load(fh)
    vtt_filename = os.path.basename(Utils.get_captions_path(video_metadata))
    vtt_filepath = '{}/{}'.format(app_args.dir, vtt_filename)
    chats = impartus.get_chats(video_metadata)
    video_id = video_metadata['ttid'] if video_metadata.get('ttid') else video_metadata['fcid']
    Captions.save_as_captions(video_id, video_metadata, chats, vtt_filepath)


def download_document():
    with open(app_args.json, 'r') as fh:
        document_metadata = json.load(fh)
    doc_filename = os.path.basename(Utils.get_documents_path(document_metadata))
    doc_filepath = '{}/{}'.format(app_args.dir, doc_filename)
    impartus.download_slides(document_metadata.get('filePath'), doc_filepath)


def download():
    if app_args.subcommand == 'video':
        download_video()
    elif app_args.subcommand == 'chat':
        download_chat()
    elif app_args.subcommand == 'document':
        download_document()
    else:
        parser.print_help()


app = sys.argv[0]
epilog_login = """
Returns user JWT token.

example: 
./{app} login
""".format(app=app)

epiog_subjects = """
Returns a json list containing subject data.

example:
./{app} subjects [-o dir]
""".format(app=app)

epilog_lectures = """
Returns a json list containing lecture videos info.

example:
./{app} lectures -j subject.json [-o dir]
""".format(app=app)

epilog_documents = """
Returns a json list containing backpack documents info.

example:
./{app} documents -j subject.json [-o dir]
""".format(app=app)

epilog_download_video = """
Download a lecture video

example:
./{app} download video -j lecture.json -o dir
"""

epilog_download_chat = """
Download chat for a lecture

example:
./{app} download chat -j lecture.json -o dir
"""

epilog_download_document = """
Download a document.

example:
./{app} download document -j document.json -o dir
""".format(app=app)

epilog = """
The CLI requires that the following variables are exported in the environment:
IMPARTUS_USER
IMPARTUS_PASS

Once logged in, users would need to export
IMPARTUS_TOKEN

IMPARTUS_URL may also be exported to use a server other than https://a.impartus.com
"""


def _parse_args(args: List):
    subparsers = parser.add_subparsers(dest="command", title='subcommands')

    login_parser = subparsers.add_parser('login',
                                         help="Login to Impartus.",
                                         epilog=epilog_login,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)

    subject_parser = subparsers.add_parser('subjects',
                                           help="Get list of subjects subscribed by the user.",
                                           epilog=epiog_subjects,
                                           formatter_class=argparse.RawDescriptionHelpFormatter)
    subject_parser.add_argument('-o', '--dir', help='Directory to save subjects json metadata.')

    lecture_parser = subparsers.add_parser('lectures',
                                           help="Get lecture info for a subject.",
                                           epilog=epilog_lectures,
                                           formatter_class=argparse.RawDescriptionHelpFormatter)
    lecture_parser.add_argument('-j', '--json', required=True, help='Subject json file.')
    lecture_parser.add_argument('-o', '--dir', help='Directory to save lecture json metadata.')

    document_parser = subparsers.add_parser('documents',
                                            help="Get backpack documents info for a subject.",
                                            epilog=epilog_lectures,
                                            formatter_class=argparse.RawDescriptionHelpFormatter)
    document_parser.add_argument('-j', '--json', required=True, help='Subject json file.')
    document_parser.add_argument('-o', '--dir', help='Directory to save document json metadata.')

    download_parser = subparsers.add_parser('download',
                                            help="Download a video/chat/document.",
                                            formatter_class=argparse.RawDescriptionHelpFormatter)
    download_subparsers = download_parser.add_subparsers(dest="subcommand", title='subcommands')

    video_dl_parser = download_subparsers.add_parser('video',
                                                     help="Download lecture video.",
                                                     epilog=epilog_download_video,
                                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    video_dl_parser.add_argument('-j', '--json', required=True, help='Lecture json.')
    video_dl_parser.add_argument('-q', '--quality', default='highest', help='Video quality (default=highest).')
    video_dl_parser.add_argument('-o', '--dir', required=True, help='Output mkv file')

    chat_dl_parser = download_subparsers.add_parser('chat',
                                                    help="Download lecture chat.",
                                                    epilog=epilog_download_chat,
                                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    chat_dl_parser.add_argument('-j', '--json', required=True, help='Lecture json.')
    chat_dl_parser.add_argument('-o', '--dir', required=True, help='Output vtt file')

    document_dl_parser = download_subparsers.add_parser('document',
                                                        help="Download backpack document.",
                                                        epilog=epilog_download_document,
                                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    document_dl_parser.add_argument('-j', '--json', required=True, help='Document json file.')
    document_dl_parser.add_argument('-o', '--dir', required=True, help='Output file')

    return parser.parse_args(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Impartus CLI.',
                                     epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    app_args = _parse_args(sys.argv[1:])

    impartus_url = os.environ.get('IMPARTUS_URL')
    if not impartus_url:
        impartus_url = 'https://a.impartus.com'
    Variables().set_login_url(impartus_url)

    if app_args.command == 'login':
        username = os.environ.get('IMPARTUS_USER')
        password = os.environ.get('IMPARTUS_PASS')
        if not username:
            error("IMPARTUS_USER needed.")
            sys.exit(1)
        if not password:
            error("IMPARTUS_PASS needed.")
            sys.exit(1)

        Variables().set_login_email(username)
        Variables().set_login_password(password)
        impartus = Impartus()

    else:
        token = os.environ.get('IMPARTUS_TOKEN')
        if not token:
            error("IMPARTUS_TOKEN needed.")
            sys.exit(1)
        impartus = Impartus(token)

    if vars(app_args).get('command'):
        globals()[app_args.command]()
    else:
        parser.print_help()
