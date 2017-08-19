![Gazee](/public/images/logo.png)

Gazee is a comic viewer for the web browser.

Read your favorite digital comics from almost any web connected device.

Works best with [Mylar](https://github.com/evilhero/mylar) comic book management, but not needed.

Gazee is still under active development and at this time should be considered an Alpha while the base features are hammered out.

## Requirements
* Python 3.6
* CherryPy
* Mako
* xmltodict
* Pillow
* rarfile

Requirements can be installed easily in the setup section below.

#### Unrar Downloads

Unrar needs to be installed and visible in the path of the user Gazee is running under to be able to properly extract all CBRs.

Double check this on Windows, different systems have different requirements for making sure you have unrar visbile in your users path.

[Windows](http://www.rarlab.com/download.htm)

[Centos](https://www.rpmfind.net/linux/rpm2html/search.php?query=unrar) needs Unrar from RPMFusion, not Offical/EPEL unar application. unar is out of date and will fail with certain types of cbrs and other rar archives.

[Debian](https://packages.debian.org/jessie/unrar)

## Setup

    cd <directory you want to install to>
    git clone https://github.com/hubbcaps/gazee.git
    cd gazee
    sudo pip install -r requirements.txt
    python Gazee.py


Go to <your-ip>:4242

Default user and pass for the web interface is admin/gazee

Proceed to the settings page and change your admin pass, and enter the path to your comic library and optionally your Mylar DB for better comic info extraction.

## Daemonize (Linux only)

You can easily run the program in Daemon mode by using the -d flag

    python Gazee.py -d

### QOL Features on the Roadmap

These are features that will make Gazee better and more up to par in what should be expected of a modern comic reader, but aren't needed for actual usability.

- [ ] Bookmarks/Remember where user was in comic.
- [ ] Add more options for gathering comic metadata than parsing ComicInfo in archive and using Mylar DB if available.
- [ ] Random First Issue of a series in library.
- [ ] OPDS Support.
- [ ] User set color changes.
- [ ] User set image sizes.
- [ ] [Mylar](https://github.com/evilhero/mylar) integration and API sharing.
