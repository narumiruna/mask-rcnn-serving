import grpc
import numpy as np
from PIL import Image, ImageDraw

import serving_pb2
import serving_pb2_grpc
from utils import load_bytes_image, rect_to_roi

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default='example.jpg')
    args = parser.parse_args()

    with open(args.image, 'rb') as f:
        img = f.read()

    channel = grpc.insecure_channel('localhost:50051')
    stub = serving_pb2_grpc.ObjectDetectionStub(channel)
    objects = stub.Detect(serving_pb2.DetectionRequest(image=img))

    img = Image.open(args.image).convert('RGB')

    for o in objects:
        print(o.label)
        print(o.rect)
        print(o.rect.x)
        # print(o.segmentation)

        draw = ImageDraw.Draw(img)
        draw.rectangle(rect_to_roi(o.rect))
        bitmap = load_bytes_image(o.segmentation, mode='1')
        draw.bitmap(((0, 0)), bitmap, fill='red')
        img.save('example_result.jpg')


if __name__ == '__main__':
    main()
