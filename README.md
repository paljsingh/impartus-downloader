Impartus Downloader
===
(see demo video at: https://www.youtube.com/watch?v=CYk_dgyso1E)

Downloader for impartus streaming videos.

- Convert impartus lectures to mkv files.
- Multiview supported. Tested with files up to 4 views.
- Tested on Mac and Linux (ubuntu).
- 


### Setup virtualenv (optional)
	$ virtualenv venv
	$ source venv/bin/activate 

### Clone repo
	$ git clone https://github.com/paljsingh/impartus-downloader.git
	$ cd impartus-downloader

### Install dependencies
	$ pip3 install -r requirements.txt


Install ffmpeg
> mac: ```brew install ffmpeg```
> 
> linux (ubuntu): 
> ```sudo apt-get install ffmpeg```
> 
> windows: [https://ffmpeg.org/download.html ](https://ffmpeg.org/download.html)
> 

Install geckodriver
> mac: ```brew install geckodriver```
> 
> linux (ubuntu): ```sudo apt-get install firefox-geckodriver```
> 
> windows:
> [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases)
> Download the release tarball and follow installation instruction.
> 

### Run application.

``` $ python3 impartus.py```

This will launch a new firefox application, and open the impartus.com page.
Login, and download the videos. Once the download is complete, the application
will start processing the offline streams saved in browser cache and convert it
to mkv.

This output files will be saved to a target_dir specified in yaml.conf, the
sub-directory organization and naming convention can be changed using available
placeholders (see yaml.conf).

Drop a mail to paljsingh@gmail.com for any issues/errors.


### TODO
- Chrome implementation.
- Auto download ppt/pdf.
- Fix occasional crash with parallel downloads. 
- Test on Windows.
- Auto-clear browser cache when running low.
- Reconcile with local storage and automatically download new lectures.
