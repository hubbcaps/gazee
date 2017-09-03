FROM python:3.6.2-alpine
RUN useradd abc -u PUID -g PGID && \
  mkdir /comics && \
	mkdir /mylar && \
	mkdir /certs && \
	apk add --no-cache git build-base python-dev py-pip jpeg-dev zlib-dev unrar && \
	git clone https://github.com/hubbcaps/gazee.git /gazee
WORKDIR /gazee
RUN pip install -r requirements.txt
RUN chown -R PUID:PGID /gazee
USER PUID
WORKDIR /gazee
CMD python Gazee.py
