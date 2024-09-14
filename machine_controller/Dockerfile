FROM python:3.9-slim-bookworm
WORKDIR /srv/acm/vending/machine_controller/
RUN apt-get update -y
RUN apt-get install -y build-essential cmake git
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip install RPi.GPIO
RUN apt-get clean
COPY . .
CMD ["/bin/bash", "python3", "-m" , "flask", "run", "--host", "0.0.0.0"]