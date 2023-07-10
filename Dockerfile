FROM python:3.10

#WORKDIR /usr/src/app
#WORKDIR ./

#COPY requirements.txt ./
COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

# forward request and error logs to docker log collector
#RUN ln -sf /dev/stdout app.log \
#	&& ln -sf /dev/stderr app.log

CMD [ "python", "-u", "./main.py" ]