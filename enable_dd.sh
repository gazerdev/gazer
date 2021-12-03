# clone latest deepdanbooru
git clone https://github.com/KichangKim/DeepDanbooru.git
cd DeepDanbooru

# install deepdanbooru and tensorflow requirements
source venv/bin/activate
python setup.py install
pip install --upgrade pip
pip install tensorflow
pip install scikit-image

# fetch pretrained model
cd ..
wget https://github.com/KichangKim/DeepDanbooru/releases/download/v4-20200814-sgd-e30/deepdanbooru-v4-20200814-sgd-e30.zip
unzip deepdanbooru-v4-20200814-sgd-e30.zip -d dd_pretrained
rm deepdanbooru-v4-20200814-sgd-e30.zip
