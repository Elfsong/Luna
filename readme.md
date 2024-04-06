# Hello, welcome to Luna 🌙

## For Cisco Readers(TL;DR)
```shell
# Set up dockers

# Open your brower
```


## For NUS Readers

### Step 0. Git Repo Preparation
```shell
# Pull the repo to local
git clone https://github.com/Elfsong/Luna.git

# Checkout to the branch 'docker'
git checkout docker
```

### Step 1. Built a Docker Image and Push it to Docker Hub
```shell
# Enter the workspace
cd ./deployment

# Docker Login (You have to register an account on https://hub.docker.com/)
docker login 

# Docker Image Bulid
docker build -t luna .

# Check the Image
docker images

# Start a Docker Container
# E.g. `docker run -p 9000:9000 -v ./data:/data -dit luna:latest`
docker run -p [LOCAL_PORT]:[DOCKER_PORT] -v [LOCAL_VOLUME]:/data -dit [IMAGE_ID]

# Check the Container
docker ps -a

# Commit the Container
# e.g. `docker commit -a "elfsong mingzhe@nus.edu.sg" -m "init" luna luna:1.0`
docker commit -a "[YOUR NAME] [YOUR EMAIL]" -m "[COMMIT_MESSAGE]" [CONTAINER_ID] [CONTAINER_TAG]

# Tag the Image
docker tag luna:1.0 elfsong/luna:1.0

# Push the Image to DockerHub
docker push elfsong/luna:1.0

# Update and Push the Latest Tag (optional)
docker tag elfsong/luna:1.0 elfsong/luna
docker push elfsong/luna
```

### Step 2. Set up the Docker Image Anywhere
```shell
# Set up Luna
# E.g. `docker run -p 9000:9000 -v ./data:/data -dit elfsong/luna:latest`
docker run -p [LOCAL_PORT]:[DOCKER_PORT] -v [LOCAL_VOLUME]:/data -dit elfsong/luna:latest

# Set up NN Filter
# E.g. docker run --gpus '"device=3"' -p 8088:80 -v /raid/hpc/mingzhe/transformers_cache:/data ghcr.io/huggingface/text-generation-inference:1.4 --model-id Elfsong/mouadsfilter
docker run --gpus '"device=[GPU_DEVICES]"' -p [LOCAL_PORT]:80 ghcr.io/huggingface/text-generation-inference:1.4 --model-id Elfsong/mouadsfilter
```

### Step 3. Open your browser
* Open `http://localhost:[DOCKER_PORT]` in your browser.
* Fill all fields.
* You are all set.