# Mask R-CNN Serving

## Build and run with CPU

```
$ docker build -t asia.gcr.io/linker-mrcnn-serving .
$ docker run -it --rm -p 50051:50051 asia.gcr.io/linker-mrcnn-serving
```

### Build and run with GPU

```
$ docker build -t asia.gcr.io/linker-mrcnn-serving:gpu -f Dockerfile.gpu .
$ nvidia-docker run -it --rm -p 50051:50051 asia.gcr.io/linker-mrcnn-serving:gpu
```
