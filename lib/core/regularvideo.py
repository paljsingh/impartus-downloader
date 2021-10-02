from lib.metadataparser import MetadataDictParser
from lib.variables import Variables
from lib.video import Video


class RegularVideo(Video):

    def __init__(self, subjects, session, timeouts):
        super().__init__(subjects, session, timeouts)

    def get_lectures(self):
        root_url = Variables().login_url()
        for subject in self.subjects:
            response = self.session.get('{}/api/subjects/{}/lectures/{}'.format(
                root_url, subject.get('subjectId'), subject.get('sessionId')),
                timeout=self.timeouts
            )

            if response.status_code == 200:
                videos_by_subject = response.json()
                for video_metadata in videos_by_subject:
                    video_id = video_metadata['ttid']
                    is_flipped = False
                    yield video_id, MetadataDictParser.add_new_fields(video_metadata), is_flipped
