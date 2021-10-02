import os
import re
import requests
from lib.variables import Variables


class BackpackSlides:

    def __init__(self, token, timeouts, logger, conf):
        self.token = token
        self.timeouts = timeouts
        self.logger = logger
        self.conf = conf

    def download_slides(self, file_url, filepath):
        root_url = Variables().login_url()

        if str(file_url).startswith('http'):
            urls = re.findall(r'(https?://\S+)', file_url)
        else:
            urls = ['{}/{}'.format(root_url, file_url)]

        download_status = False
        for slides_url in urls:
            ext = slides_url.split('.')[-1].lower()
            if ext not in self.conf.get('allowed_ext'):
                self.logger.warning('Downloading {}. Files of type {} not allowed, see config.'.format(
                    slides_url, ext))
                continue

            self.logger.info('Downloading document from {}'.format(slides_url))
            response = requests.get(
                slides_url,
                timeout=self.timeouts,
                headers={'Cookie': 'Bearer={}'.format(self.token)}
            )
            if response.status_code == 200:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                with open(filepath, 'wb+') as fh:
                    fh.write(response.content)
                download_status = True
            else:
                self.logger.error('Error fetching slides from url: {}'.format(file_url))
                self.logger.error('Http response code: {}, response body: {}: '.format(
                    response.status_code, response.text))
        return download_status
