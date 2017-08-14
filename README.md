# Gazee

![Gazee](/public/images/logo.png)

Gazee is a comic viewer for the web browser.

Read your favorite digital comics from almost any web connected device.

Gazee is still under active development and at this time should be considered an Alpha while the base features are hammered out.

## Requirements
* Python 3.6
* CherryPy
* Mako
* xmltodict
* Pillow
* rarfile

#### Unrar Downloads

Unrar needs to be installed and visible in the path of the user Gazee is running under to be able to properly extract all CBRs.

[Windows](http://www.rarlab.com/download.htm)

[Centos 7](https://www.rpmfind.net/linux/rpm2html/search.php?query=unrar) needs Unrar from RPMFusion, not Offical/EPEL unar application. unar is out of date and will fail with certain types of cbrs and other rar archives.

[Debian](https://packages.debian.org/jessie/unrar)

## Setup

    cd <your install directory>
    git clone https://github.com/hubbcaps/gazee.git
    cd gazee
    sudo pip install -r requirements.txt
    python Gazee.py

Proceed to the settings page and enter the path to your comic library and optionally your Mylar DB for better comic info extraction.

## Daemonize (*nix only)

You can easily run the program in Daemon mode by using the -d flag

    python Gazee.py -d

## Current Status

### Completed features

- [x] Frontend base mako templates.
- [x] Landing page with Recent Comics view
- [x] Comic Scanner for building the DB and creating image cache
- [x] Reading view, including changing pages with instruction pane.
- [x] Parent Directory / Child Associations
- [x] Build out Library View one above is done.
- [x] Add compression for the cache images.
- [x] Settings Page allowing basic server configuration.
- [x] Authentication Mechanism
- [x] Ability to change admin/user password.
- [x] Multi User Support with Admin/User Settings. 
- [x] Mylar DB support for additional comic info
- [x] Daemonize. Make it runable as a service.
- [x] Portability, is able to run under *nix and windows 

### Needed features before Gazee is actually usable

- [ ] Search capabilities
- [ ] Allow use of keybinds for changing pages in Reading view
- [ ] Add more options for gathering comic metadata than parsing ComicInfo in archive and using Mylar DB if available.

### QOL Features on the Roadmap

These are features that will make Gazee better and more up to par in what should be expected of a modern comic reader, but aren't needed for actual usability.

- [ ] Random First Issue of a series in library.
- [ ] OPDS Support
- [ ] User set color changes.
- [ ] [Mylar](https://github.com/evilhero/mylar) integration and API sharing.
