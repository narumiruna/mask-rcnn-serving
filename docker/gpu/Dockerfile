FROM nvidia/cuda:9.0-cudnn7-devel

ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update && apt-get install -y \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext-dev \
    libxrender-dev \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pip==9.0.3 \
    && pip3 install -U \
    cython==0.28.3 \
    googleapis-common-protos==1.5.3 \
    grpcio-tools==1.13.0 \
    h5py==2.8.0 \
    imgaug==0.2.6 \
    keras==2.2.0 \
    numpy==1.14.5 \
    opencv-python==3.4.1.15 \
    Pillow==5.2.0 \
    scikit-image==0.13.0 \
    scipy==1.1.0 \
    tensorflow-gpu==1.9.0 \
    && pip3 install --no-deps -e git+https://github.com/narumiruna/Mask_RCNN.git#egg=mask-rcnn \
    && rm -rf ~/.cache/pip

WORKDIR /workspace
RUN git clone https://github.com/narumiruna/mask-rcnn-serving.git /workspace \
    && python3 setup.py install

RUN wget https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5

ENTRYPOINT [ "python3", "-m", "mask_rcnn_serving.server" ]
