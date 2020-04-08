echo "Install Apt Package !"
apt-get install -y python3 python3-pip python-opencv

echo "Install Python Package !"
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "Install Finished !"
