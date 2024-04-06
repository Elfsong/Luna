# Hello, welcome to Luna 🌙

## For Cisco Readers (TL;DR)

* Download **data** from [the link](https://mynbox.nus.edu.sg/u/ttsM25_bDPCk2wz1/435f6f30-4a25-4504-b946-c2ecc5aa877c?l). Hope you have the [access code](mailto:mingzhe@nus.edu.sg).

* Unzip and place **data** at [SOMEWHERE]. 

* Run `docker run -p 9000:9000 -v [SOMEWHERE]:/data -dit elfsong/luna:latest`

* Run `docker run --gpus '"device=0"' -p [FILTER_PORT]:80 -v [SOMEWHERE]:/data -dit ghcr.io/huggingface/text-generation-inference:1.4 --model-id Elfsong/mouadsfilter`
    * The first time run might take more than 10 minutes to downlode model weights.

* Open your browser at `http://[YOUR_IP_ADDRESS]:9000`. 
    * OpenAI Token can be found at: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
    * NN Filter URL: http://[YOUR_IP_ADDRESS]:[FILTER_PORT]
    * Upload new `metadata` and `notes` replacing the default NUS data.
    * Select whether you intend to use case filters.

* Then, you're all set 🥳.

## For NUS Readers

This is the minimal version of **Luna**.

At the very beginning, you need to prepare a runnable computer. 

**Luna** itself can run across different systems (Windows / Linux / MacOS), but the **NN filter** requires Nvidia GPUs. Therefore, you need a `Nvidia GPU Server` if you intend to enable the **NN filter**.

**Luna** and **NN filter** have been dockerized. You can set up the **Luna** container anywhere, and the **NN filter** on a `Nvidia GPU Server`.

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
# E.g. `docker run -p 9000:9000 -v ./data:/data --name my_luna -dit luna:latest`
docker run -p [LOCAL_PORT]:[DOCKER_PORT] -v [LOCAL_VOLUME]:/data --name [CONTAINER_NAME] -dit [IMAGE_ID]

# Check the Container
docker ps -a

# Commit the Container
# e.g. `docker commit -a "elfsong mingzhe@nus.edu.sg" -m "init" my_luna luna:1.0`
docker commit -a "[YOUR NAME] [YOUR EMAIL]" -m "[COMMIT_MESSAGE]" [CONTAINER_NAME] [CONTAINER_TAG]

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

## FAQ
### Q1: docker: permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Post "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/create": dial unix /var/run/docker.sock: connect: permission denied.
sudo chmod 666 /var/run/docker.sock
