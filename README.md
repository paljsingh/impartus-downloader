Impartus Downloader
===

Downloader for impartus streaming videos.
---

- Convert impartus lectures to mkv files.
- Regular and flipped lecture download supported.
- Tested on Mac OSX, Linux (ubuntu) and Windows 10.
- Parallel downloads supported. 
- Pause / Resume individual downloads.
- Supports multi-track files. Tested with video lectures having up to 4 tracks.
- Backpack slides download supported.
-  🆕 Pyside2/Qt5 based ui.
-  🆕 Bypass login screen to access previously downloaded content.
-  🆕 Content Search.
- Attach slides downloaded from external sources to the lecture folder.
-  🆕 Option to view all the attached slides from the UI.
-  🆕 Better management of the downloaded content.
- Lecture chats overlayed as closed captions for the video.
-  🆕 Download chats / captions file separately.
- Editable subject field to use shorter subject names and better organize the folders.
- Auto Organize lectures to match any change in lecture topic, subject. 
-  🆕 Fast, Responsive UI.
-  🆕 Supports system themes.
- Sortable content.
- 🆕 Better looking widgets.
- 🆕 Round progress bar.
- Configurable columns.


---

### UI
Dark theme
![Impartus Downloader - Dark theme](ui/images/dark-theme.png)

Light theme
![Impartus Downloader - Dark theme](ui/images/light-theme.png)


### Demo video
[TBA]
---

## Prerequisites

python >= v3.6
ffmpeg >= v4.3

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
> ![Setting background opacity in VLC](ui/images/vlc-bg-opacity.png "Setting background opacity in VLC")
>
> Below is a sample output of the opacity change.
>
> ![Background Opacity](ui/images/bg-opacity.png "Background Opacity")
> 
---

**System theme settings not picked up on Linux**

On linux, PySide2 must be installed as system-wide package to access the currently selected theme settings.
A pip based installation falls back to Fusion theme, and won't pick up the run time changes in the theme settings.

Steps needed in order to use system theme settings on linux.

remove pip Pyside2 installation:
```
$ pip3 uninstall PySide2
```

also remove any system wide Pyside2 pip install
```
$ sudo pip3 uninstall PySide2
```

Qt5ct is not needed, so just ensure the current envrionment does NOT have the Qt5ct variable
```
$ env | grep QT_QPA_PLATFORMTHEME
```
The above command should show empty result.

Install PySide2 and dependent components as system wide package.

```
$ sudo apt-get install python3-pyside2.qtuitools python3-pyside2.qtwidgets libpyside2-py3-5.14
```

Ensure to use PySide2 api, in case there also exists a Qt5/Qt4 installation,
```
$ echo 'export QT_API=PySide2' >> ~/.bashrc 
$ source ~/.bashrc
$ python3 App.py
```
alternatively, one can run the app as:
```
$ QT_API=PySide2 python3 App.py
```

Ref: [PySimpleGUI/PySimpleGUI#2437](https://github.com/PySimpleGUI/PySimpleGUI/issues/2437)

---


Drop a mail to paljsingh@gmail.com in case of any issues/errors.
