## Docker

**Purpose:**
Run apps in isolated containers so they are easy to install, start/stop,
upgrade, and survive reboots.

---

### Install Docker Engine + Docker Compose

This installs Docker from Docker's official repository.

``` bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg |   sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg]   https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" |   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update

sudo apt install -y docker-ce docker-ce-cli containerd.io   docker-buildx-plugin docker-compose-plugin
```

Enable Docker at boot:

``` bash
sudo systemctl enable --now docker
```

Allow your user to run Docker without `sudo`:

``` bash
sudo usermod -aG docker $USER
newgrp docker
```

Verify installation:

``` bash
docker --version
docker compose version
```

---

### Common Commands

List running containers:

``` bash
docker ps
```

View logs:

``` bash
docker logs -n 200 <container>
```

Restart container:

``` bash
docker restart <container>
```

Stop & remove container:

``` bash
docker rm -f <container>
```

Pull image:

``` bash
docker pull <image:tag>
```

---

### Updating a Container (Manual `docker run`)

``` bash
docker pull <image:tag>
docker rm -f <container>
# re-run your docker run command
```

If you are using volumes, your data is preserved.

---

### Updating a Docker Compose App

``` bash
docker compose pull
docker compose up -d
```

This recreates containers with the latest images while keeping
persistent volumes intact.
