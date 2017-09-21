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
#  along with Gazee.  If not, see <http://www.gnu.org/licenses/>.

from gazee.gazee import Gazee
from gazee.comicscan import ComicScanner
import gazee.authmech
import gazee.db
import gazee.config

__version__ = '0.0.1'
__all__ = ['Gazee', 'ComicScanner']

FULL_PATH = ""
DB_FILE = 'gazee.db'
DATA_DIR = 'data'
TEMP_DIR = 'tmp'
PIDFILE = '/tmp/gazee.pid'

PORT = 4242
COMIC_PATH = ''
COMIC_SCAN_INTERVAL = 60
COMICS_PER_PAGE = 15
MYLAR_DB = ''
SSL_KEY = ''
SSL_CERT = ''
WEB_TEXT_COLOR = 'FFFFFF'
MAIN_COLOR = '757575'
ACCENT_COLOR = 'BDBDBD'
LOGO = 'static/images/logos/red/logo-red-yellow.png'
THUMB_SIZE = 400, 300
LOG_LEVEL = 'logging.INFO'
ARGS = []

