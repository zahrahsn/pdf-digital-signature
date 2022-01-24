FROM ubuntu:18.04
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && \
    apt install -y python3-dev python3-pip

RUN apt install -y libglib2.0-0 libsm6 libxrender-dev libxext6 gcc g++ mupdf

RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

#COPY ./entrypoint.sh .
#RUN sed -i 's/\r$//g' entrypoint.sh
#RUN chmod +x entrypoint.sh

COPY . .