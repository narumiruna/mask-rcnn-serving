FROM ubuntu:16.04

ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update && apt-get install -y \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install -U pip==9.0.3 \
    && pip3 install -U -r requirements.txt \
    && rm -rf ~/.cache/pip \
    && rm requirements.txt

WORKDIR /workspace

COPY mrcnn /workspace/mrcnn
RUN wget https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5

COPY detector.py .
COPY detection_server.py .
COPY utils.py .

COPY serving.proto .
COPY serving_pb2.py .
COPY serving_pb2_grpc.py .

ENTRYPOINT [ "python3", "detection_server.py" ]


