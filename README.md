# Gazee

![Gazee](/public/images/logo.png)

Gazee will be a webapp for reading your comics in your web browser.

Eventually you will be able to start it up, point it at your library directory and have fun!

## Requirements
* Python 3.6
* CherryPy
* Mako
* xmltodict
* Pillow
* rarfile

unrar needs to be installed and visible in the path of the user Gazee is running under.

#### Unrar Downloads

[Windows](http://www.rarlab.com/download.htm)

[Centos 7](https://centos.pkgs.org/7/forensics-x86_64/unrar-5.3.0-1.el7.x86_64.rpm.html)

[Debian](https://packages.debian.org/jessie/unrar)

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

### Needed features before Gazee is actually usable

- [ ] Add more options for gathering comic metadata than parsing ComicInfo in archive.
- [ ] Portability. Verify working on Windows. Currently developed and working under linux.
- [ ] Daemonize. Make it runable as a service.
- [ ] Various system level settings need to be implemented for CherryPy still.

### QOL Features on the Roadmap

These are features that will make Gazee better and more up to par in what should be expected of a modern comic reader, but aren't needed for actual usability.

- [ ] Allow use of keybinds for changing pages in Reading view
- [ ] OPDS Support
- [ ] User set color changes.
- [ ] [Mylar](https://github.com/evilhero/mylar) integration and API sharing.
