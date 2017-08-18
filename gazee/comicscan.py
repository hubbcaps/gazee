#  This file is part of Gazee.
#
#  Gazee is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Gazee is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Mylar.  If not, see <http://www.gnu.org/licenses/>.

import os
import sqlite3
import zipfile
import rarfile
import zlib
import xmltodict
import logging
import threading

from pathlib import Path
from PIL import Image

import gazee

logging.basicConfig(level=logging.DEBUG, filename='data/gazee.log')
logger = logging.getLogger(__name__)

# This class will hold the various methods needed to fill out the Directory Table and the Comics table in the DB.


class ComicScanner(object):

    # This method will handle scanning the directories and returning a list of them all.
    def dirScan(self):
        logging.info("Dir Scan Requested")
        full_paths = []
        full_paths.append(gazee.COMIC_PATH)
        for root, dirs, files in os.walk(gazee.COMIC_PATH):
            full_paths.extend(os.path.join(root, d) for d in dirs)

        logging.info("Dir Scan Completed")
        logging.info("%i Dirs Found" % (len(full_paths)))
        return full_paths

    # This method will handle scanning the comics and returning a list of them all.
    def comicScan(self):
        logging.info("Comic Scan Requested")
        full_paths = []
        for root, dirs, files in os.walk(gazee.COMIC_PATH):
            for f in files:
                if f.endswith((".cbz", ".cbr")):
                    full_paths.append(os.path.join(root, f))

        logging.info("Comic Scan Completed")
        logging.info("%i Comics Found" % (len(full_paths)))
        return full_paths

    # This method takes an argument of the full comic path and will simply unpack the requested comic into the temp directory. It first checks if there are already files in the temp directory. If so, it removes all of them and then unpacks the comic. It doesn't return anything currently, and will be used for both scanning and reading comics.
    def buildUnpackComic(self, comic_path):
        logging.info("%s unpack requested" % comic_path)
        for root, dirs, files in os.walk(os.path.join(gazee.TEMP_DIR, "build"), topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
        for root, dirs, files in os.walk(os.path.join(gazee.TEMP_DIR, "build"), topdown=False):
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        if comic_path.endswith(".cbr"):
            opened_rar = rarfile.RarFile(comic_path)
            opened_rar.extractall(os.path.join(gazee.TEMP_DIR, "build"))
        elif comic_path.endswith(".cbz"):
            opened_zip = zipfile.ZipFile(comic_path)
            opened_zip.extractall(os.path.join(gazee.TEMP_DIR, "build"))
        return

    def userUnpackComic(self, comic_path, user):
        logging.info("%s unpack requested" % comic_path)
        for root, dirs, files in os.walk(os.path.join(gazee.TEMP_DIR, user), topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
        for root, dirs, files in os.walk(os.path.join(gazee.TEMP_DIR, user), topdown=False):
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        if comic_path.endswith(".cbr"):
            opened_rar = rarfile.RarFile(comic_path)
            opened_rar.extractall(os.path.join(gazee.TEMP_DIR, user))
        elif comic_path.endswith(".cbz"):
            opened_zip = zipfile.ZipFile(comic_path)
            opened_zip.extractall(os.path.join(gazee.TEMP_DIR, user))
        return

    # This method will return a list of .jpg files in their numberical order to be fed into the reading view.
    def readingImages(self, user):
        logging.info("Image List Requested")
        image_list = []
        for root, dirs, files in os.walk(os.path.join(gazee.TEMP_DIR, user)):
            for f in files:
                if f.endswith((".png", ".gif", ".bmp", ".dib", ".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".tiff", ".tif")):
                    image_list.append(os.path.join(root, f))
                    image_list.sort()
        logging.info("Image List Created")
        return image_list

    # This method takes an argument of the comic name, it then looks in the temp directory after comic has been upacked for an image with 000, 001 and an image extnesion in the name. This image name and it's path are stored in variables, then makes directory named after them, and pushes the file into that directory. It then returns the path to that file to be inserted into the DB as the comics image in the library and recent comic views.
    def imageMove(self, comic_name, volume_number, issue_number):
        logging.info("Thumbnail Requested")
        image_temp_path = []
        image = []
        sorted_files = []

        for root, dirs, files in os.walk(os.path.join(gazee.TEMP_DIR, "build")):
            sorted_files.extend(os.path.join(root, usf) for usf in files)

        sorted_files.sort()

        for f in sorted_files:
            if f.endswith((".png", ".gif", ".bmp", ".dib", ".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".tiff", ".tif")):
                image_temp_path = f
                image_split = os.path.split(f)
                image = image_split[-1]
                break

        absPath = os.path.abspath(os.path.join(gazee.DATA_DIR, "cache", comic_name, volume_number, issue_number))

        if not os.path.exists(absPath):
            os.makedirs(absPath)

        if len(image) == 0:
            logging.info("Image Not Found")
            image_dest = 'static/images/imgnotfound.png'
        else:
            image_dest = os.path.join(gazee.DATA_DIR, "cache", comic_name, volume_number, issue_number, image)

            if not os.path.exists(image_dest):
                try:
                    im = Image.open(image_temp_path)
                    im.thumbnail(gazee.THUMB_SIZE)
                    im.save(image_dest)
                    logging.info("Thumbnail Saved")
                except IOError:
                    logging.info("Thumbnail Generation failed")
                    image_dest = 'static/images/imgnotfound.png'

        logging.info("Thumbnail Generated")
        return image_dest

    # This method will parse the XML for our values we'll insert into the DB for the comics info such as name, issue number, volume number and summary.
    def comicInfoParse(self, comicpath):
        logging.info("Comic Info Requested")
        comic_name = "Not Available"
        comic_issue = "Not Available"
        comic_volume = "Not Available"
        comic_summary = "Not Available"

        unpackedFiles = []
        comic_attributes = {}

        for root, dirs, files in os.walk(os.path.join(gazee.TEMP_DIR, "build")):
            unpackedFiles.extend(os.path.join(root, f) for f in files)
        logging.info("%i unpacked files found" % (len(unpackedFiles)))

        for f in unpackedFiles:
            if any(x in f for x in ("ComicInfo", "Comicinfo" "comicInfo", "comicinfo", ".xml")):
                logging.info("ComicInfo File Found")
                with open(f) as fd:
                    comic_attributes = xmltodict.parse(fd.read())
                    try:
                        comic_name = comic_attributes['ComicInfo']['Series']
                    except:
                        comic_name = "Not Available"
                    try:
                        comic_issue = comic_attributes['ComicInfo']['Number']
                    except:
                        comic_issue = "Not Available"
                    try:
                        comic_volume = comic_attributes['ComicInfo']['Volume']
                    except:
                        comic_volume = "Not Available"
                    try:
                        comic_summary = comic_attributes['ComicInfo']['Summary']
                    except:
                        comic_summary = "Not Available"
                    break

        if not gazee.MYLAR_DB == "":
            try:
                location = os.path.basename(comicpath)
                connection = sqlite3.connect(gazee.MYLAR_DB)
                c = connection.cursor()

                c.execute('SELECT * FROM issues WHERE location=?', (location,))
                comic_attributes = c.fetchone()

                if comic_attributes is not None:
                    if comic_name == "Not Available":
                        logging.info("Mylar DB Found and Being Used")
                        comic_name = comic_attributes[1]
                        comic_issue = comic_attributes[3]

                connection.close()
            except:
                logging.info("Mylar DB is locked or doesn't exist")
        logging.info("ComicInfo Being Returned")
        return {'name': comic_name, 'issue': comic_issue, 'volume': comic_volume, 'summary': comic_summary}

    # This method is where the magic actually happens. This will use all the previous functions to build out our two DB tables, Directories and Comics respectively.
    def dbBuilder(self):

        logging.info("DB Build Requested")
        logging.info("Begining Full Directory and Comic Scan")
        # Here we set the db file path.
        db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

        # Here we make the inital DB connection that we will be using throughout this function.
        connection = sqlite3.connect(str(db))
        c = connection.cursor()

        # Here we define some variables we will use to check for existing directories and directories that need to be removed from the db.
        c.execute('SELECT * FROM {tn}'.format(tn=gazee.ALL_DIRS))
        pathsInDB = c.fetchall()
        dictOfParents = []
        keyNames = ['ParentKey', 'Path']
        # Convert tuple to list
        dictOfParents = [dict(zip(keyNames, tup)) for tup in pathsInDB]
        logging.info("Grabbed Directories Currently in DB")

        # Here we call the dirScan directory to get a list of all the directories under the set comic directory.
        logging.info("Requesting Directory Scan")
        directories = self.dirScan()
        logging.info("Directory Scan Returned")

        # Here we check if the Directory listings in the DB still exists on disk, if not, we remove them and their children from the db.
        for d in dictOfParents:
            for key, value in d.items():
                if key == 'Path':
                    if value not in directories:
                        logging.info("Removing Directories No Longer on Disk.")
                        c.execute('DELETE FROM {tn} WHERE {cn}=?'.format(tn=gazee.ALL_DIRS, cn=gazee.FULL_DIR_PATH), (d['Path'],))
                        c.execute('DELETE FROM {tn} WHERE {cn}=?'.format(tn=gazee.DIR_NAMES, cn=gazee.PARENT_KEY), (d['ParentKey'],))

        # Here we iterate over the scanned directories and check if any match any of the earlier returned paths. If they do, we skip to the next scanned directory, otherwise we insert them.
        for d in directories:
            if d in [dic['Path'] for dic in dictOfParents]:
                logging.debug("Directory exists in DB, Skipping")
                continue
            else:
                logging.info("Adding Directory %s to DB" % (d))
                c.execute('INSERT INTO {tn} ({cn1}) VALUES (?)'.format(tn=gazee.ALL_DIRS, cn1=gazee.FULL_DIR_PATH), (d,))

        # Here we commit real quick to make sure our main Dir table is up to date for associating the proper parent keys to their child contents in the regular directory table.
        # We also reset our parent dictionary.
        connection.commit()

        c.execute('SELECT * FROM {tn}'.format(tn=gazee.ALL_DIRS))
        pathsInDB = c.fetchall()
        dictOfParents = []
        keyNames = ['ParentKey', 'Path']
        # Convert tuple to list
        dictOfParents = [dict(zip(keyNames, tup)) for tup in pathsInDB]

        c.execute('SELECT * FROM {tn}'.format(tn=gazee.DIR_NAMES))
        namesInDB = c.fetchall()
        namesOfDirs = []
        # Convert tuple to list
        namesOfDirs = [tup[0] for tup in namesInDB]

        for d in dictOfParents:
            dirContents = os.listdir(d['Path'])
            for dc in dirContents:
                if dc in namesOfDirs:
                    logging.info("Dir Name exists, skipping")
                    continue
                elif os.path.isdir(os.path.join(d['Path'], dc)):
                    logging.info("Dir name %s being added to DB" % (dc))
                    c.execute('INSERT INTO {tn} ({cn1}, {cn2}) VALUES (?,?)'.format(tn=gazee.DIR_NAMES, cn1=gazee.NICE_NAME, cn2=gazee.PARENT_KEY), (dc, d['ParentKey']))
                else:
                    continue

        connection.commit()

        # Here we define some variables we will use to check for existing comics and comics that need to be removed from the db.
        logging.info("Gathering all Comics in DB")
        c.execute('SELECT ({col}) FROM {tn}'.format(col=gazee.COMIC_FULL_PATH, tn=gazee.ALL_COMICS))
        comicPathsInDB = c.fetchall()
        listOfComicPaths = []
        # Convert tuple to list
        listOfComicPaths = [tup[0] for tup in comicPathsInDB]

        # Here we call comic scan and get the paths of all comics to iterate over.
        logging.info("Comic Scan Requested")
        all_comics = self.comicScan()
        logging.info("Comic Scan Returned")

        # Here we check if the Directory listings in the DB still exists on disk, if not, we remove them from the db.
        for f in listOfComicPaths:
            if f not in all_comics:
                logging.info("Comic Being Removed from DB")
                c.execute('DELETE FROM {tn} WHERE {cn}=?'.format(tn=gazee.ALL_COMICS, cn=gazee.COMIC_FULL_PATH), (f,))

        # Here we start iterating, inside we'll call the rest of the functions, gather the rest of the info and then insert it a row at a time into the DB.
        for f in all_comics:
            if f in listOfComicPaths:
                logging.info("Comic exists in DB, Skipping")
                continue
            else:
                try:
                    logging.info("Unpacking Comic")
                    self.buildUnpackComic(f)
                    logging.info("Unpacking Successful")
                except (zipfile.BadZipFile, rarfile.RarWarning, zlib.error, rarfile.BadRarFile, rarfile.RarCRCError, OSError) as e:
                    logging.info("Unpacking Failed")
                    logging.info(str(e))
                    continue

                logging.info("Comic Info being requested")
                info = self.comicInfoParse(f)
                logging.info("Comic Info Successfully returned")
                # After unpacking the comic, we now assign the values returned to variables we can use in our insert statement.
                name = info['name']
                issue = info['issue']
                volume = info['volume']
                summary = info['summary']

                # Here we call the image move method with the previously retrieved comic name as its argument. This returns the image path to be stored in the coming insert function.
                image = self.imageMove(name, volume, issue)

                pk = 1
                bp = os.path.split(f)
                parent = bp[0]
                for d in dictOfParents:
                    if parent == d['Path']:
                        pk = d['ParentKey']

                logging.info("Comic %s Being Inserted into DB" % (name))
                c.execute('INSERT INTO {tn} ({cn}, {ci}, {cv}, {cs}, {cimg}, {cp}, {pk}, {it}) VALUES (?, ?, ?, ?, ?, ?, ?, DATE("now"))'.format(tn=gazee.ALL_COMICS, cn=gazee.COMIC_NAME, ci=gazee.COMIC_NUMBER, cv=gazee.COMIC_VOLUME, cs=gazee.COMIC_SUMMARY, cimg=gazee.COMIC_IMAGE, cp=gazee.COMIC_FULL_PATH, pk=gazee.PARENT_KEY, it=gazee.INSERT_DATE), (name, issue, volume, summary, image, f, pk))
                connection.commit()
                logging.info("Comic %s Inserted into DB Successfully" % (name))

        connection.commit()
        connection.close()

        logging.info("DB Build succesful")
        return

    def rescanDB(self):
        self.dbBuilder()
        threading.Timer((int(gazee.COMIC_SCAN_INTERVAL) * 60), self.rescanDB).start()
