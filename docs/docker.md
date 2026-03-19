# Docker

## Purpose

Install Docker Engine and Docker Compose on the Ubuntu VM so the containerized
parts of the stack can run and restart automatically.

## Run Location

Ubuntu VM.

## Before You Start

- The [Ubuntu VM](ubuntu-virtual-machine.md#ubuntu-virtual-machine) is created
  and reachable over SSH
- The VM user has `sudo` access
- The Ubuntu package repositories are reachable from the VM

## Context

LiteLLM and OpenWebUI run in Docker containers in this project. The Python
applications use virtual environments and systemd instead.

## Steps

### Step 1: Install Docker repository prerequisites

```bash
sudo apt update
```

```bash
sudo apt install -y ca-certificates curl gnupg
```

```bash
sudo install -m 0755 -d /etc/apt/keyrings
```

### Step 2: Add Docker's official apt repository

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

```bash
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Step 3: Install Docker Engine and Compose

```bash
sudo apt update
```

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Step 4: Enable Docker at boot

```bash
sudo systemctl enable --now docker
```

### Step 5: Allow the VM user to run Docker without `sudo`

```bash
sudo usermod -aG docker "$USER"
```

Apply the new group membership in the current shell:

```bash
newgrp docker
```

### Step 6: Validate the installation

```bash
docker --version
```

```bash
docker compose version
```

```bash
docker ps
```

## What You Just Set Up

Docker is now installed on the VM and starts automatically at boot. The VM user
can run Docker commands without `sudo`, and the environment is ready for the
LiteLLM and OpenWebUI setup pages.
