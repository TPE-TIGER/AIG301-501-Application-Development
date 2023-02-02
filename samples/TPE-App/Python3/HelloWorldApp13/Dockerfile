FROM amd64/python:3.7.11-slim-stretch
ENV APP hello-app
COPY . /${APP}
WORKDIR /${APP}
RUN pip3 install -r requirements.txt
WORKDIR /${APP}/app

CMD ["/bin/bash", "./run.sh" ]
