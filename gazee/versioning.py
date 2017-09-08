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

import os
import logging
import git

import gazee


def current_version():
    repo = git.Repo(os.path.dirname(gazee.FULL_PATH))
    local_commit = repo.commit()
    return local_commit.hexsha


def latest_version():
    repo = git.Repo(os.path.dirname(gazee.FULL_PATH))
    remote = repo.remotes.origin
    info = remote.fetch()[0]
    remote_commit = info.commit
    return remote_commit.hexsha


def update_app():
    logging.basicConfig(level=logging.DEBUG, filename=os.path.join(gazee.DATA_DIR, 'gazee.log'))
    logger = logging.getLogger(__name__)
    current_commit = current_version()
    latest_commit = latest_version()

    if current_commit == latest_commit:
        logger.info("No update needed")
        return False

    if current_commit != latest_commit:
        logger.info("Updated Needed")

        os.rename('public/css/style.css', 'public/css/style.css.bak')

        repo = git.Repo(os.path.dirname(gazee.FULL_PATH))
        o = repo.remotes.origin
        try:
            o.pull()
        except git.exc.GitCommandError:
            logger.exception('Failed to pull version')
            os.rename('public/css/style.css.bak', 'public/css/style.css')
            return False

        if os.path.exists('public/css/style.css'):
            with open('public/css/style.css', 'r+') as f:
                style = f.read()
                f.seek(0)
                style = style.replace("757575", gazee.MAIN_COLOR)
                style = style.replace("BDBDBD", gazee.ACCENT_COLOR)
                style = style.replace("FFFFFF", gazee.WEB_TEXT_COLOR)
                f.write(style)
                f.truncate()

            os.remove('public/css/style.css.bak')
        else:
            os.rename('public/css/style.css.bak', 'public/css/style.css')

        logger.info("Update Pulled")
        return True
