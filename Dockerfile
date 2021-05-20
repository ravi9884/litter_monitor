ARG PYTHON_VERSION_SHORT=3.7
ARG OPENCV_VERSION=4.4.0
ARG CPU_CORES=4

FROM python:${PYTHON_VERSION_SHORT}-slim

ARG DEBIAN_FRONTEND=noninteractive

# Installing build tools and dependencies.
# More about dependencies there: https://docs.opencv.org/4.0.0/d2/de6/tutorial_py_setup_in_ubuntu.html
RUN set -e; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        apt-utils \
        build-essential; \
    apt-get install -y --no-install-recommends \
        # Downloading utils
        unzip \
        wget \
        # Build utils
        cmake \
        gcc \
        # Required dependencies
        python-numpy \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libgstreamer-plugins-base1.0-dev \
        # Optional dependencies
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libopenexr-dev \
        libtiff-dev \
        libwebp-dev \
        # Video device drivers
        libv4l-dev \
        libdc1394-22-dev; \
    # Clear apt cache
    rm -rf /var/lib/apt/lists/*

RUN pip install numpy

ARG OPENCV_VERSION
ENV OPENCV_VERSION=$OPENCV_VERSION

# Download latest source and contrib
RUN set -e; \
    cd /tmp; \
    wget -c -nv -O opencv.zip https://github.com/opencv/opencv/archive/$OPENCV_VERSION.zip; \
    unzip opencv.zip; \
    wget -c -nv -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/$OPENCV_VERSION.zip; \
    unzip opencv_contrib.zip

ARG PYTHON_VERSION_SHORT
ENV PYTHON_VERSION=$PYTHON_VERSION_SHORT

ARG CPU_CORES

# Build opencv
RUN set -e; \
    cd /tmp/opencv-$OPENCV_VERSION; \
    mkdir build; \
    cd build; \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
        -D OPENCV_EXTRA_MODULES_PATH=/tmp/opencv_contrib-$OPENCV_VERSION/modules \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        # Build without GUI support
        -D WITH_QT=OFF \
        -D WITH_GTK=OFF \
        # Build without GPU support
        -D WITH_OPENCL=OFF \
        -D WITH_CUDA=OFF \
        -D BUILD_opencv_gpu=OFF \
        -D BUILD_opencv_gpuarithm=OFF \
        -D BUILD_opencv_gpubgsegm=OFF \
        -D BUILD_opencv_gpucodec=OFF \
        -D BUILD_opencv_gpufeatures2d=OFF \
        -D BUILD_opencv_gpufilters=OFF \
        -D BUILD_opencv_gpuimgproc=OFF \
        -D BUILD_opencv_gpulegacy=OFF \
        -D BUILD_opencv_gpuoptflow=OFF \
        -D BUILD_opencv_gpustereo=OFF \
        -D BUILD_opencv_gpuwarping=OFF \
        # Build with python
        -D BUILD_opencv_python3=ON \
        -D BUILD_opencv_python2=OFF \
        -D PYTHON_DEFAULT_EXECUTABLE=$(which python${PYTHON_VERSION}) \
        -D OPENCV_SKIP_PYTHON_LOADER=ON \
        -D OPENCV_PYTHON3_INSTALL_PATH=$(python${PYTHON_VERSION} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
        # Ignore all unnecessary stages
        -D BUILD_opencv_apps=OFF \
        -D BUILD_EXAMPLES=OFF \
        -D INSTALL_C_EXAMPLES=OFF \
        -D INSTALL_PYTHON_EXAMPLES=OFF \
        -D BUILD_DOCS=OFF \
        -D BUILD_PERF_TESTS=OFF \
        -D BUILD_TESTS=OFF \
        ..; \
    make -j$CPU_CORES; \
    make install; \
    ldconfig; \
    # Clean up
    make clean; \
    cd /tmp; \
    rm -rf /tmp/*

RUN pip3 install pytz==2020.5
RUN pip3 install numpy
RUN pip3 install python-roku==3.1.5
RUN pip3 install PlexAPI==4.2.0
RUN pip3 install paho-mqtt==1.5.1
RUN pip3 install matplotlib
RUN pip3 install -U pip
RUN pip3 install python-dotenv
RUN pip3 install jupyter

RUN apt-get update && apt-get install -y git
RUN mkdir -p /root/.ssh
RUN git config --global user.email "6249312+ravi9884@users.noreply.github.com"
RUN git config --global user.name "Ravi Ramadoss"
RUN ssh-keyscan github.com >> ~/.ssh/known_hosts


COPY cred/id_rsa /root/.ssh/id_rsa
COPY cred/id_rsa.pub /root/.ssh/id_rsa.pub
RUN chmod 700 /root/.ssh/id_rsa
RUN chmod 700 /root/.ssh/id_rsa.pub

RUN git clone git@github.com:ravi9884/machine-learning-portfolio.git /root/machine-learning-portfolio
WORKDIR /root/machine-learning-portfolio/litter-monitor/app

RUN python3 setup.py develop
COPY startup.sh /root
COPY app/.env /root/machine-learning-portfolio/litter-monitor/app
COPY jupyter_notebook_config.py /root/.jupyter/
RUN chmod +x /root/startup.sh
ENTRYPOINT [ "sh", "-c", "/root/startup.sh ${STORAGE_DIR} ${CAMERA_JPG_URL} ${ROKU_IP} \"${PLEX_CLIENT_NAME}\" ${PLEX_SERVER_NAME} ${PLEX_LIBRARY_NAME} ${MQTT_BROKER} ${INTERVAL} ${START_TIME} ${END_TIME} ${CONTEXT_URL}" ]
