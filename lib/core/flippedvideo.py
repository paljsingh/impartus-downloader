from datetime import datetime, timedelta

from lib.metadataparser import MetadataDictParser
from lib.variables import Variables
from lib.video import Video


class FlippedVideo(Video):

    def __init__(self, subjects, session, timeouts):
        super().__init__(subjects, session, timeouts)

    def get_lectures(self):
        root_url = Variables().login_url()
        for subject in self.subjects:
            response = self.session.get('{}/api/subjects/flipped/{}/{}'.format(
                root_url, subject.get('subjectId'), subject.get('sessionId')),
                timeout=self.timeouts
            )
            if response.status_code == 200:
                categories = response.json()
                for category in categories:

                    # flipped lectures do not have lecture sequence number field, generate seq-no setting the oldest
                    # lecture with seq-no=1. By default impartus portal return lectures with highest ttid/fcid first.
                    num_lectures = len(category['lectures'])
                    for i, lecture in enumerate(category['lectures']):
                        # cannot update the original dict while in loop, shallow copy is fine for now.
                        flipped_lecture = lecture.copy()
                        flipped_lecture['ttid'] = 0
                        flipped_lecture['seqNo'] = num_lectures - i
                        flipped_lecture['slideCount'] = 0
                        flipped_lecture['createdBy'] = ''  # duplicate info, present elsewhere.

                        start_time = datetime.strptime(lecture['startTime'], '%Y-%m-%d %H:%M:%S')
                        end_time = start_time + timedelta(0, lecture['actualDuration'])
                        flipped_lecture['endTime'] = end_time.strftime("%Y-%m-%d %H:%M:%S")

                        video_id = flipped_lecture['fcid']
                        is_flipped = True
                        yield video_id, MetadataDictParser.add_new_fields(flipped_lecture), is_flipped
