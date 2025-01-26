#

## setup



### 2. ros2 build
```shell
sudo apt install python3-vcstool
vcs import ros2_ws/src < packages.repos

cd ./ros2_ws
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
```

### 3. python virtual env

```shell
python3.9 -m venv env
source env/bin/activate
python3.9 -m pip install -r torch-req.txt --index-url https://download.pytorch.org/whl/cu118
python3.9 -m pip install -r requirements.txt

```

### 1. recording
```shell
## terminal 1
source ros2_ws/install/setup.bash
ros2 launch recording_launch recording.launch.xml 

## terminal 2
source ros2_ws/install/setup.bash
ros2 service call /set_recording std_srvs/srv/SetBool "{data: true}"

ros2 service call /set_recording std_srvs/srv/SetBool "{data: false}"
```

### 2. processing data
```shell
python3 processing.py -i /home/arata22/dataset/recording/ -o  /media/arata22/AT_2TB/dataset/my_record/ -r

python3 


```

