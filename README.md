Impartus Downloader
===
(see demo video at: https://www.youtube.com/watch?v=CYk_dgyso1E)

Downloader for impartus streaming videos.

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
- Chrome implementation.
- Auto download ppt/pdf.
- Fix occasional crash with parallel downloads. 
- Auto-clear browser cache when running low.
- Reconcile with local storage and automatically download new lectures.
