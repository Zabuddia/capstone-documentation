# Ubuntu Virtual Machine

## Purpose: 
Host web applications and AI services including LiteLLM, OpenWebUI, RAG Website, and an MCP Server.

**Host / location:** Microsoft Azure

**OS version:** Ubuntu Server 24.04

**IPs / networking:**

* Configured with a Public IP (set to allow during setup, subject to change once configured)
* Basic NIC network security group
* Public inbound ports allowed: SSH

**Services Running:**

* LiteLLM
* Open WebUI
* Rag Website
* MCP Server

**Startup / systemd:**

* Docker Services (OpenWebUI, LiteLLM): Managed via Docker with `--restart unless-stopped` policies (or Docker Compose) so they survive reboots.

* Python Services (RAG Website, MCP Server): Managed via systemd service files running from the Python virtual environment (`venv`) to ensure automatic startup.

**Operational notes:**

* Hardware Profile: Standard_B2s (2 vCPUs, 4 GiB memory).
* Authentication: SSH public key. The private key requires restricted permissions to connect.


## 1) Create the Azure Virtual Machine

1. Navigate to Virtual Machines in the Azure portal and click **+ Create**.
2. Basics Tab:
    * Select your appropriate Subscription & Resource group.
    * Create a Virtual machine name.
    * Select **Ubuntu Server 24.04** for the Image.
    * Select **Standard_B2s** (2 vcpus, 4 GiB memory) for the Size.
    * Choose **SSH public key** for Authentication type and name the key.
    * Allow selected ports for Public inbound ports, and select **SSH**.
3. Networking Tab:
    * Select a virtual network.
    * Allow **Public IP** for setup (change it once configured).
    * Set NIC network security group to **Basic**.
    * Allow selected ports for Public inbound ports, and select **SSH**.
4. Click **Review + create**. Make sure to download your private key file when prompted.

## 2) Connect to the VM

1. In your local terminal, restrict the permissions on your private key file so it is secure:
  `chmod 400 your-key-name.pem`
2. In Azure, navigate to **Connect** on the left side bar 
3. Under SSH command, copy and paste this command in your local terminal 

## 3) Upload Files

1. Open another local terminal that is not linked to the VM 
2. Run command to upload your desired files:
  `scp -i your-key.pem -r /path/to/your/project azureuser@<PUBLIC-IP>:/home/azureuser/`
3. In the terminal connected to the VM, install python:
  `sudo apt update` 
  `sudo apt install git python3 python3-pip python3-venv –y`