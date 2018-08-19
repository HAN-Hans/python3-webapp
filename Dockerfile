FROM python:3.6-alpine

RUN adduser -D webasyncio
USER webasyncio

WORKDIR /home/webasyncio

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/dev.txt
RUN source venv/bin/activate
COPY www www

# run-time configuration
EXPOSE 5000
ENTRYPOINT ["venv/bin/python", "www/app.py"]
