FROM ubuntu:16.04

ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libavcodec-dev \
    libavformat-dev \
    libdc1394-22-dev \
    libjasper-dev \
    libjpeg-dev \
    libpng-dev \
    libswscale-dev \
    libtbb-dev \
    libtiff-dev \
    pkg-config \
    python3-numpy \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install OpenCV
ENV OPENCV_VERSION 3.4.1
ENV OPENCV_CONTRIB_VERSION 3.4.1

RUN (cd /tmp \
    && wget --quiet -O- https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.tar.gz | tar -xz \
    && wget --quiet -O- https://github.com/opencv/opencv_contrib/archive/${OPENCV_CONTRIB_VERSION}.tar.gz | tar -xz \
    && mkdir -p opencv-${OPENCV_VERSION}/build \
    && cd opencv-${OPENCV_VERSION}/build \
    && cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DOPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-${OPENCV_CONTRIB_VERSION}/modules \
    -DBUILD_opencv_python3=ON \
    -DPYTHON3_EXECUTABLE=$(which python3) \
    -DWITH_CUDA=OFF \
    .. \
    && make -j$(nproc) install) \
    && rm -rf /tmp/*

COPY requirements.txt .
RUN pip3 install -U pip==9.0.3 \
    && pip3 install -U -r requirements.txt \
    && rm -rf ~/.cache/pip \
    && rm requirements.txt

WORKDIR /workspace

COPY mrcnn .
COPY detector.py .
COPY detection_server.py .
COPY utils.py .
COPY serving.proto .
COPY serving_pb2.py .
COPY serving_pb2_grpc.py .

RUN wget https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5

ENTRYPOINT [ "python3", "detection_server.py" ]
