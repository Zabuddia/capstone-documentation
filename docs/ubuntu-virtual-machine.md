# Ubuntu Virtual Machine

## Purpose

Create the Ubuntu VM that hosts the private application stack:

- LiteLLM
- OpenWebUI
- RAG Website
- MCP Server

## Run Location

Azure portal for VM creation, a local machine for SSH and `scp`, and the Ubuntu
VM for package installation.

## Before You Start

- An Azure Government subscription and resource group
- An SSH public key, or a plan to generate one during VM creation
- Permission to create compute and networking resources in the subscription

## Context

This VM is the host for the rest of the stack. Later pages assume the working
directories live under `/home/<VM_USER_NAME>/` and that internal services are
reached over WireGuard at `10.55.55.1`.

## Steps

### Step 1: Create the Azure VM

1. In the Azure portal, open **Virtual Machines** and select **Create**.
2. On the **Basics** tab:
   - Choose the correct subscription and resource group.
   - Enter a VM name.
   - Select **Ubuntu Server 24.04**.
   - Select **Standard_B2s**.
   - Choose **SSH public key** for authentication.
   - Allow public inbound port **SSH**.
3. On the **Networking** tab:
   - Use the VM virtual network.
   - Set the NIC network security group to **Basic**.
   - Allow a public IP during setup.
   - Keep public inbound access limited to SSH.
4. Review the configuration and create the VM.
5. Download the private key if Azure generated one.

### Step 2: Connect to the VM

On the local machine, set restrictive permissions on the private key:

```bash
chmod 400 /path/to/your-key.pem
```

Connect to the VM from the local machine:

```bash
ssh -i /path/to/your-key.pem <VM_USER_NAME>@<VM_PUBLIC_IP>
```

### Step 3: Install the base packages on the VM

Run these commands on the Ubuntu VM:

```bash
sudo apt update
```

```bash
sudo apt install -y git python3 python3-pip python3-venv curl
```

### Step 4: Copy files to the VM when a later page requires it

Several later pages provide starter bundles as `.tar.gz` files. The same
pattern is used each time.

From the local machine:

```bash
scp -i /path/to/your-key.pem ~/Downloads/rag-website.tar.gz <VM_USER_NAME>@<VM_PUBLIC_IP>:/home/<VM_USER_NAME>/
```

On the Ubuntu VM after the upload finishes:

```bash
tar -xzf ~/rag-website.tar.gz -C ~/
```

## What You Just Set Up

The Ubuntu VM is now ready for the remaining setup pages. SSH access is in
place, the base packages are installed, and later pages can add services under
the VM user account.
