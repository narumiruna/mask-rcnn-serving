import argparse
import os

import grpc
import numpy as np
from PIL import Image, ImageDraw

import serving_pb2
import serving_pb2_grpc
import utils


def main():
    try:
        os.remove('example_result.jpg')
    except:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default='example.jpg')
    args = parser.parse_args()

    with open(args.image, 'rb') as f:
        img = f.read()

    channel = grpc.insecure_channel('localhost:50051')
    stub = serving_pb2_grpc.ObjectDetectionStub(channel)
    objects = stub.DetectStream(serving_pb2.DetectionRequest(image=img))

    img = Image.open(args.image).convert('RGB')

    for o in objects:
        print(o.label)
        print(o.box)

        draw = ImageDraw.Draw(img)
        draw.rectangle(utils.rect_to_roi(o.box), outline='blue')
        draw.line(xy=o.shape.series, fill='red')

    img.save('example_result.jpg')


if __name__ == '__main__':
    main()
