FROM python:3.6.2-alpine
RUN mkdir /data && \
	mkdir /mylar && \
	mkdir /certs && \
	apk add --no-cache git build-base python-dev py-pip jpeg-dev zlib-dev && \
	git clone https://github.com/hubbcaps/gazee.git /gazee
WORKDIR /gazee
RUN pip install -r requirements.txt
CMD python Gazee.py