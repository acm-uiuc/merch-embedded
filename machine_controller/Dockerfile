FROM python:3.9.20-bookworm
WORKDIR /srv/acm/vending/machine_controller/
RUN apt-get update -y
RUN apt-get install -y build-essential python3-dev bash
RUN pip install RPi.GPIO
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN cd VL53L0X_rasp_python && make && cd ..
CMD [ "python3", "-m" , "flask", "run", "--host", "0.0.0.0"]