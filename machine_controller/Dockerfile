FROM python:3.9-slim-bookworm
WORKDIR /srv/acm/vending/machine_controller/
RUN apt-get update -y
RUN apt-get install -y build-essential cmake
RUN pip install RPi.GPIO
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . .
RUN cd VL53L0X_rasp_python && make && cd ..
RUN apt-get clean
ENV PYTHONPATH="/usr/local/lib/python3.9:/usr/local/lib/python3.9/lib-dynload:/usr/local/lib/python3.9/site-packages:/srv/acm/vending/machine_controller/VL53L0X_rasp_python/python/"
CMD [ "python3", "-m" , "flask", "run", "--host", "0.0.0.0"]