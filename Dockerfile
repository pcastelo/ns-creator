FROM python:3.9-slim

COPY . .

RUN mkdir /tmp/base/ -p
RUN cp static/fly.toml /tmp/base/

ADD static/fly.tar.gz /tmp/fly/
RUN cp /tmp/fly/bin/flyctl /usr/local/bin/

ENV PYTHON_HOST=0.0.0.0
ENV PYTHON_PORT=5000
ENV TZ America/Argentina/Buenos_Aires

RUN pip install -r requirements.txt
RUN rm -fr requirements.txt

CMD python3 -m gunicorn -b ${PYTHON_HOST}:${PYTHON_PORT} --workers=1 --threads=6 app:app

EXPOSE 5000
