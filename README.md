Impartus Downloader
===


### Clone repo
	$ git clone https://github.com/paljsingh/impartus-downloader.git

### Setup virtualenv (optional)
	$ virtualenv venv
	$ source venv/bin/activate 

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

### Install Firefox plugin

Open firefox and visit url: ```about:debugging```

Click on `This Firefox` -> `Load Temporary Add-on...`

Select `impartus-downloader` -> `addon` -> `impartus-metadata-updater` -> `manifest.json`

Click Open.

### Download videos

Visit impartus page.

Login and download any number of videos using the download icon.

Once the download shows complete Run the application.

### Run application.

``` $ python3 impartus.py```

This will decrypt, encode the offline videos and save them to the folder specified in yaml.conf

