import argparse
import os

import grpc
import numpy as np
from PIL import Image, ImageDraw

import serving_pb2
import serving_pb2_grpc
import utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default='example.jpg')
    parser.add_argument('--target', type=str, default='localhost:50051')
    args = parser.parse_args()

    with open(args.image, 'rb') as f:
        img = f.read()

    channel = grpc.insecure_channel(args.target)
    stub = serving_pb2_grpc.ObjectDetectionStub(channel)
    objects = stub.DetectStream(serving_pb2.DetectionRequest(image=img))

    img = Image.open(args.image).convert('RGB')

    for i, obj in enumerate(objects):
        # print object info
        s = 'Object: {}'.format(i + 1)
        if obj.label:
            s += ', label: {}'.format(obj.label)
        if obj.box:
            s += ', box: [{}]'.format(utils.box_to_str(obj.box))
        print(s)

        draw = ImageDraw.Draw(img)
        # draw bounding box
        if obj.box:
            draw.rectangle(utils.rect_to_roi(obj.box), outline='blue')

        # draw polygon
        if obj.shape:
            draw.polygon(xy=obj.shape.series, outline='red')

    img.show()


if __name__ == '__main__':
    main()
