FROM python:3.9

RUN mkdir /app
WORKDIR /app

ENV DB_HOST=db
ENV DB_PORT=51373
ENV DB_USER=postgres
ENV DB_NAME=playlist_bot_db
ENV DB_PASSWORD=Jbf4833Tk3Q7
ENV BOT_TOKEN=5973282021:AAHgOwStnhg7pwr4bfLar-oAb2wDtRABdfo

ADD . /app/
ADD requirements.txt requirements.txt

RUN apt update -y
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-u", "bot.py"]