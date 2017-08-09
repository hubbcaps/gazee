![Gazee Logo](/public/images/logo.png?raw=true "Gazee Logo")

Gazee will be a webapp for reading your comics in your web browser.

Eventually you will be able to start it up, point it at your library directory and have fun!

## Requirements
* Python 3.6
* CherryPy
* Mako
* PyUnpack
* patoolib
* xmltodict
* Pillow

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

### Needed features before Gazee is actually usable

- [ ] Ability to change admin/user password.
- [ ] Multi User Support with Admin/User Settings. 

### QOL Features to be added

These are features that will make Gazee better and more up to par in what should be expected of a modern comic reader, but aren't needed for actual usability.

- [ ] Allow use of keybinds for changing pages in Reading view
- [ ] OPDS Support
- [ ] User set color changes.
- [ ] [Mylar](https://github.com/evilhero/mylar) integration and API sharing.
