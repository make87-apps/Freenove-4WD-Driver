apt update && apt install -y --no-install-recommends gnupg
echo "deb http://archive.raspberrypi.org/debian/ bookworm main" > /etc/apt/sources.list.d/raspi.list \
  && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 82B129927FA3303E
apt update && apt -y upgrade && apt install -y --no-install-recommends \
         python3-picamera2 \
         libcamera-apps libcamera-dev libcamera-tools i2c-tools python3-smbus libcap-dev python3-libcamera