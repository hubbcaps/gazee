![Gazee](/public/images/logo.png)

Gazee is a comic viewer for the web browser.

Read and reach your favorite digital comics from almost any web connected device.

Works great with [Mylar](https://github.com/evilhero/mylar) comic book management, but not needed.

Check out [the Wiki](https://github.com/hubbcaps/gazee/wiki) for detailed instructions on setup if you need them.

Questions can also be asked in the #gazee channel on Freenode

## Features

Recent Comics
![screen01](http://i.imgur.com/4cRYbJP.jpg)

Exposes your sorting structure in a library view
![screen02](http://i.imgur.com/LuJDAAG.jpg)

Download your issue if you have a preferred reader outside of Gazee and read a summary of the issue in line if available with your archive
![screen03](http://i.imgur.com/NcgCQTq.jpg)

Make Gazee yours and change up the color scheme
![screen04](http://i.imgur.com/xCLoowh.jpg)
![screen05](http://i.imgur.com/F5mb0bA.jpg)

Settings overlay to make the comic feel how you want it.
![screen06](http://i.imgur.com/t0NsWMp.jpg)

HTTPS Support

Bookmarks remember where you left off as you read.

Multiple Users and Admins

Much more to come!

## Requirements
* Python 3.6
* CherryPy
* Mako
* xmltodict
* Pillow
* rarfile
* GitPython

Requirements can be installed easily in the setup section below.

#### Unrar Downloads

Unrar needs to be installed and visible in the path of the user Gazee is running under to be able to properly extract all CBRs.

Double check this on Windows, different systems have different requirements for making sure you have unrar visbile in your users path.

[Unrar for Windows](http://www.rarlab.com/rar_add.htm), windows also needs command line accessible Git installed, gone over in the [install guide on the wiki](https://github.com/hubbcaps/gazee/wiki/Windows-Install-Guide)

[Centos](https://www.rpmfind.net/linux/rpm2html/search.php?query=unrar) needs Unrar from RPMFusion, not Offical/EPEL unar application. unar is out of date and will fail with certain types of cbrs and other rar archives.

[Debian](https://packages.debian.org/jessie/unrar)

## Setup

**Step 1: Clone the repository and install python dependencies**

    cd <directory you want to install to>
    git clone https://github.com/hubbcaps/gazee.git
    cd gazee
    sudo pip install -r requirements.txt
    python Gazee.py

**Step 2: Logon to Gazee's Web UI**)

  Go to **http://your-ip:4242**
  
  Default username and password for the web interface:
  
  * **Username:** `admin`
  * **Password:** `gazee`
  
  Proceed to the settings page and change your admin pass, and enter the path to your comic library   and optionally your Mylar DB for better comic info extraction.

### Daemonize (Linux only)

You can easily run the program in Daemon mode by using the -d flag

    python Gazee.py -d

## Docker Container

[Dockerfile](./Dockerfile) associated in this repository allows you to containerize the service starting from a light weight [python:3.6.2-alpine](https://hub.docker.com/_/python/) (~30 MB). It installs all dependencies and required python packages automatically. You can find the docker image [here in docker hub](https://hub.docker.com/r/mayankt/gazee/).

**Step 1A: Pull Docker image for Gazee**

You can pull the image directly from docker hub using the following commands: 
 
 `docker pull mayankt/gazee`

**Step 1B: Build Docker image for Gazee**

Alternatively you can build your own docker image locally by entering in the following commands: 

```bash
git clone https://github.com/hubbcaps/gazee.git
cd /gazee
docker build -t mayankt/gazee .
```
**Step 2: Run docker container**

To run the container, enter the following command on your docker host: 

```
docker run -dt \
--name=gazee \
-v ${local-comics-dir}:/data \
-v ${local-mylarDB-dir}:/mylar \
-v ${local-certs-dir}:/certs \
-p 4242:4242 \
mayankt/gazee
```
**Note:** 

`-v ${local-comics-dir}:/data` is a volume mount from your local host directory where you have stored your comicbook files `${local-comics-dir}` to the `/data` directory within the container. 

`-v ${local-mylarDB-dir}:/mylar` **Optional Flag** is a volume mount from your local host directory where you have stored your mylar db `${local-mylarDB-dir}` to the `/mylar` directory within the container.

`-v ${local-certs-dir}:/certs` **Optional Flag** is a volume mount from your local host directory where you have stored your server certificate `${local-certs-dir}` to the `/certs` directory within the container.

**Step 3: Logon to Gazee's Web UI**

You can use the above volume mounts to configure the settings of the app and dictate where to find you comic library, Mylar DB, and certificates.

Go to **http://your-ip:4242**
  
  Default username and password for the web interface:
  
  * **Username:** `admin`
  * **Password:** `gazee`

### QOL Features on the Roadmap

These are features that will make Gazee better and more up to par in what should be expected of a modern comic reader, but aren't needed for actual usability.

- [ ] Random First Issue of a series in library.
- [ ] OPDS Support.
- [ ] User set image sizes.
- [ ] Notifications on new comics
- [ ] Reports on various stats of your library; number of bad archives, comics without metadata, etc etc
