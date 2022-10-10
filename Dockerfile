FROM  python:3.9-slim

COPY requirements.txt /
COPY . /app
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt --upgrade pip
ENV PYTHON_HOST=0.0.0.0
ENV PYTHON_PORT=5000
EXPOSE 5000
RUN cd app
ENV EXTRA_CMD="cd ."
CMD ${EXTRA_CMD} & python3 -m gunicorn -b ${PYTHON_HOST}:${PYTHON_PORT} --workers=1 --threads=6 app:app
