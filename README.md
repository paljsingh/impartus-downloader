Impartus Downloader
===

Downloader for impartus streaming videos.

- 🆕  Qt5 bsed ui.
- 🆕  System themes supported
- 🆕  Offline workflow to access previously downloaded lectures/slides.
- 🆕  Content search.
- 🆕  Better, responsive user experience.

- Convert impartus lectures to mkv files.
- Regular and flipped lecture download supported.
- Tested on Mac OSX, Linux (ubuntu) and Windows 10.
- Parallel downloads supported. 
- Supports multi-track files. Tested with video lectures having up to 4 tracks.
- Backpack slides download supported.
- Lecture chats overlayed as closed captions for the video.
- Pause / Resume individual downloads.
- Editable subject field to use shorter subject names and better organize the folders.
- Auto Organize lectures to match any change in lecture topic, subject. 
- Attach slides downloaded from external sources to the lecture folder.
- Sortable content.
- Customizable color schemes, fonts.
- Configurable columns.


---

### UI
![Impartus Downloader](ui/images/ui-demo.gif "Impartus Downloader")


### Demo video
[TBA]
---

## Prerequisites

python >= v3.6
ffmpeg >= v4.0

## Installation / Run

### OSX (10.14+)

>   ```
> # setup virtualenv (optional)
> $ virtualenv venv
> $ source venv/bin/activate 
>
> # clone repo
> $ git clone https://github.com/paljsingh/impartus-downloader.git
> $ cd impartus-downloader
>
> # install dependencies
> $ pip3 install -r requirements.txt
> $ brew install ffmpeg
> 
> # Ensure ffmpeg version is >= 4.3.0
> $ ffmpeg -version 
>
> # Run application
> $ python3 App.py
> ```

Windows 10
>```
> # clone repo
> $ git.exe clone https://github.com/paljsingh/impartus-downloader.git
> $ cd impartus-downloader
>
> # install dependencies
> $ pip3.exe install -r requirements.txt
>
> Download win64-gpl zip from the following link, extract and copy ffmpeg.exe to
> impartus-downloader folder. The ffmpeg.exe statically bundles the dependent libs and
> should be about 90 MB in size.
> [https://github.com/BtbN/FFmpeg-Builds/releases](https://github.com/BtbN/FFmpeg-Builds/releases)
> 
> # Ensure ffmpeg version is >= 4.3.0
> $ ffmpeg.exe -version 
>
> # Run application
> $ python.exe App.py
> ```

Linux (Ubuntu 20+)
>```
> # setup virtualenv (optional)
> $ virtualenv venv
> $ source venv/bin/activate 
>
> # clone repo
> $ git clone https://github.com/paljsingh/impartus-downloader.git
> $ cd impartus-downloader
>
> # install dependencies
> $ pip3 install -r requirements.txt
> $ sudo apt-get install ffmpeg
>
> # Ensure ffmpeg version is >= 4.3.0
> $ ffmpeg -version 
>
> # Run application
> $ python3 App.py
> ```


## Configuration

see etc/impartus.conf


## Unit Tests

> FIXME:
> 
> $ python3 -m pytest -v test
>

---

## Known Issues

**Incorrect lecture slide associated to a video**

> The impartus platform does not offer a strict video to lecture slides mapping, the application uses the upload dates of the two for a fuzzy match. 
> 
> You may try changing (decreasing) the value of `slides_upload_window` value in `etc/impartus.conf`, which may work better in case you have more than one lectures for a subject within a week's duration.
>
---

**Connection issues when downloading**
>
> Impartus site may start throttling the connections if there are too many parallel downloads. The application uses retry logic with induced delay. However, if the issue persists you may need to restart the app.
> 
---

**Application crashes on Linux**

> On some systems the application crashes with error:
> `X Error of failed request:  BadLength (poly request too large or internal Xlib length error)`
>
> The issue is caused by a bug in libXft and can be resolved by uninstalling `fonts-noto-color-emoji`
>
>  `$ sudo apt-get remove fonts-noto-color-emoji`
>
---

**Hard to read closed captions on white background**
> 
> With VLC, you can set the background opacity value to 255.
> 
>  Go to Preferences.
> 
>  Select 'All' settings
> 
>  Navigate to Video > Subtitle / OSD > Text renderer   
> 
>  Change 'Background Opacity' to 255
> 
>  Save and restart VLC.
> 
> ![Setting background opacity in VLC](etc/vlc-bg-opacity.png "Setting background opacity in VLC")
>
> Below is a sample output of the opacity change.
>
> ![Background Opacity](etc/bg-opacity.png "Background Opacity")
> 
---


Drop a mail to paljsingh@gmail.com in case of any issues/errors.
