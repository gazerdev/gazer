# Old Python because of Tensorflow 
FROM python:3.8-slim

WORKDIR /usr/src/gazer
COPY . .

RUN pip install -r requirements.txt && python setup.py install

# DeepDanbooru support:
RUN apt-get update && apt-get -y --no-install-recommends install wget unzip git 
RUN git clone https://github.com/KichangKim/DeepDanbooru.git deepdanbooru && cd deepdanbooru && pip install .[tensorflow]
RUN cd deepdanbooru && wget https://github.com/KichangKim/DeepDanbooru/releases/download/v4-20200814-sgd-e30/deepdanbooru-v4-20200814-sgd-e30.zip && unzip deepdanbooru-v4-20200814-sgd-e30.zip -d dd_pretrained && rm deepdanbooru-v4-20200814-sgd-e30.zip

EXPOSE 5000
CMD [ "python", "gazer" ]
