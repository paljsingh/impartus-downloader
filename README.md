Impartus Downloader
===

(see demo video at: https://www.youtube.com/watch?v=CYk_dgyso1E)

### Setup virtualenv (optional)
	$ virtualenv venv
	$ source venv/bin/activate 

### Clone repo
	$ git clone https://github.com/paljsingh/impartus-downloader.git
	$ cd impartus-downloader

### Install dependencies
	$ pip3 install -r requirements


Install ffmpeg
> mac: ```brew install ffmpeg```
> 
> linux: 
> ```yum install ffmpeg``` or
> ```apt-get install ffmpeg```
> 
> windows: [https://ffmpeg.org/download.html ](https://ffmpeg.org/download.html)
> 

Install geckodriver
> mac: ```brew install geckodriver```
> 
> linux, windows:
> [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases)
> Download the release tarball and follow installation instruction.
> 

### Run application.

``` $ python3 impartus.py```

This will launch a new firefox application, and open the impartus.com page.
Login, and download the videos. Once the download is complete, the application
will start processing the offline streams saved in browser cache and convert it
to mp4.

This output files will be saved to a target_folder specified in yaml.conf, the
sub-directory organization and naming convention can be changed using available
placeholders (see yaml.conf).

Drop a mail to paljsingh@gmail.com for any issues/errors.



