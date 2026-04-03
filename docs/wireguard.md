# WireGuard

## Purpose

Configure the Ubuntu VM as a WireGuard VPN gateway so the internal services can
be reached over the private address `10.55.55.1`.

---

## Run Location

Ubuntu VM unless a step explicitly says to use the Azure portal or a client
device.

---

## Before You Start

- The [Ubuntu VM](ubuntu-virtual-machine.md#ubuntu-virtual-machine) is created
  and reachable over SSH
- The VM public IP is available

---

## Context

The WireGuard tunnel uses the subnet `10.55.55.0/24`. The VM listens as
`10.55.55.1`, and the rest of the documentation assumes the private services
are reached through that address instead of the public internet.

---

## Steps

### Step 1: Install WireGuard on the Ubuntu VM

```bash
sudo apt update
```

```bash
sudo apt install -y wireguard-tools
```

### Step 2: Generate the server key pair

Create the `/etc/wireguard` directory and generate the keys directly into it:

```bash
sudo mkdir -p -m 700 /etc/wireguard
wg genkey | sudo tee /etc/wireguard/server_private.key | wg pubkey | sudo tee /etc/wireguard/server_public.key > /dev/null
sudo chmod 600 /etc/wireguard/server_private.key
```

You will need these values in the next steps:

```bash
cat /etc/wireguard/server_private.key   # paste into wg0.conf
cat /etc/wireguard/server_public.key    # give to each VPN client
```

### Step 3: Create the server configuration

Open the configuration file:

```bash
sudo nano /etc/wireguard/wg0.conf
```

Paste the following template and replace the placeholders:

```ini
[Interface]
Address = 10.55.55.1/24
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY>

PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -s 10.55.55.0/24 -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -s 10.55.55.0/24 -o eth0 -j MASQUERADE

[Peer]
PublicKey = <CLIENT_1_PUBLIC_KEY>
AllowedIPs = 10.55.55.2/32

[Peer]
PublicKey = <CLIENT_2_PUBLIC_KEY>
AllowedIPs = 10.55.55.3/32
```

Each client needs its own `[Peer]` block. On the server, `AllowedIPs` should
normally be the specific client address, such as `10.55.55.2/32`.

### Step 4: Enable IPv4 forwarding

```bash
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-wireguard.conf
```

```bash
sudo sysctl --system
```

### Step 5: Allow WireGuard through the Azure NSG

1. Go to your virtual machine in the Azure portal.
2. In the left menu under **Settings**, click **Networking**.
3. Click **Add inbound security rule**.

Add the following two rules:

**WireGuard rule**

| Field | Value |
|---|---|
| Source | Any |
| Source port ranges | * |
| Destination | Any |
| Service | Custom |
| Destination port ranges | 51820 |
| Protocol | UDP |
| Action | Allow |
| Priority | 310 |
| Name | AllowWireguard |

**SSH rule** (should already exist — edit it to restrict the source)

| Field | Value |
|---|---|
| Source | IP Addresses |
| Source IP addresses/CIDR ranges | Your company's allowed IP addresses |
| Destination | Any |
| Protocol | TCP |

### Step 6: Start WireGuard and enable it at boot

```bash
sudo systemctl enable --now wg-quick@wg0
```

```bash
sudo systemctl status wg-quick@wg0
```

```bash
sudo wg show
```

If `wg0.conf` changes later, restart the service:

```bash
sudo systemctl restart wg-quick@wg0
```

### Step 7: Configure a client (Windows)

#### 1. Install WireGuard

Download and install WireGuard for Windows from the official installer at [wireguard.com/install](https://www.wireguard.com/install/).

#### 2. Create a tunnel and generate keys

1. Open the WireGuard app.
2. Click **Add Tunnel** → **Add empty tunnel**.
3. The app generates a private key and public key automatically. The private key is filled in for you — do not share it.
4. Copy the **public key** that appears at the top of the tunnel editor.
5. Send the public key to the server administrator so they can add it as a `[Peer]` block in `/etc/wireguard/wg0.conf` on the VM.

!!! note "Wait for confirmation"
    Do not activate the tunnel until the administrator confirms your public key
    has been added to the server and WireGuard has been restarted.

#### 3. Configure the tunnel

In the tunnel editor, replace the contents with the following and fill in the placeholders:

```ini
[Interface]
PrivateKey = <CLIENT_PRIVATE_KEY>
Address = 10.55.55.2/32
DNS = 8.8.8.8

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = <VM_PUBLIC_IP>:51820
AllowedIPs = 10.55.55.0/24
PersistentKeepalive = 25
```

- Replace `10.55.55.2` with your assigned client VPN IP.
- `<SERVER_PUBLIC_KEY>` is the contents of `/etc/wireguard/server_public.key` on the VM.
- `<VM_PUBLIC_IP>` can be found on the **Overview** page of the VM in the Azure portal.
- `AllowedIPs = 10.55.55.0/24` is split-tunnel mode — only traffic destined for the VPN subnet routes through WireGuard.

Click **Save**.

#### 4. Activate the tunnel

Click **Activate** in the WireGuard app. The status should change to **Active**.

### Step 8: Validate the connection

From the client device, open a terminal and ping the VPN gateway:

```bash
ping 10.55.55.1
```

From the Ubuntu VM, confirm the client handshake:

```bash
sudo wg show
```

The VM should show a recent handshake for the client peer after the tunnel comes up.

### Step 9: Optional full-tunnel mode

To send all client traffic through the VM, change this line in the client
configuration:

```ini
AllowedIPs = 0.0.0.0/0
```

Keep IPv4 forwarding and the NAT rules enabled if full-tunnel mode is used.

---

## What You Just Set Up

WireGuard now provides private access to the Ubuntu VM and the services bound
to `10.55.55.1`. The rest of the application stack can stay off the public
internet and still be reachable from approved client devices.
