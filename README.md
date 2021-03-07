Impartus Downloader
===
Downloader for impartus streaming videos.

Demo video:
[![Impartus v2.0 demo](https://img.youtube.com/vi/V5pcdUtiRjw/0.jpg)](https://www.youtube.com/watch?v=V5pcdUtiRjw)

- Convert impartus lectures to mkv files.
- Multiview supported. Tested with files up to 4 views.
- Tested on Mac, Linux (ubuntu) and Windows 10.
- 

### Setup virtualenv (optional)
	$ virtualenv venv
	$ source venv/bin/activate 

### Clone repo
	$ git clone https://github.com/paljsingh/impartus-downloader.git
	$ cd impartus-downloader

### Install dependencies

  mac/linux:    
	$ pip3 install -r requirements.txt

  windows:
	$ pip3.exe install -r requirements.txt



Install ffmpeg
> mac: ```brew install ffmpeg```
> 
> linux (ubuntu): 
> ```sudo apt-get install ffmpeg```
> 
> windows:
> [https://github.com/BtbN/FFmpeg-Builds/releases](https://github.com/BtbN/FFmpeg-Builds/releases)
> 
> Download ffmpeg win64 zip, extract and copy ffmpeg.exe to current folder.
> 

### Run application.

``` $ python3 App.py```

### Configuration
see yaml.conf 


Drop a mail to paljsingh@gmail.com for any issues/errors.


### TODO
- Auto download ppt/pdf.
- Better UI and feedback.
- Logging improvements.
- 
