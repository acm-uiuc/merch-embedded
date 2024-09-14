FROM python:3.9-slim-bookworm
WORKDIR /srv/acm/vending/machine_controller/
RUN apt-get update -y
RUN apt-get install -y build-essential cmake git
RUN pip install RPi.GPIO
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . .
RUN apt-get clean
CMD ["/bin/bash", "python3", "-m" , "flask", "run", "--host", "0.0.0.0"]