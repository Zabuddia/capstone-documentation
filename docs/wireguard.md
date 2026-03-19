# WireGuard

## Purpose

Configure the Ubuntu VM as a WireGuard VPN gateway so the internal services can
be reached over the private address `10.55.55.1`.

## Run Location

Ubuntu VM unless a step explicitly says to use the Azure portal or a client
device.

## Before You Start

- The [Ubuntu VM](ubuntu-virtual-machine.md#ubuntu-virtual-machine) is created
  and reachable over SSH
- The VM public IP is available
- Permission is available to edit the VM network security group in Azure

## Context

The WireGuard tunnel uses the subnet `10.55.55.0/24`. The VM listens as
`10.55.55.1`, and the rest of the documentation assumes the private services
are reached through that address instead of the public internet.

## Steps

### Step 1: Install WireGuard on the Ubuntu VM

```bash
sudo apt update
```

```bash
sudo apt install -y wireguard wireguard-tools
```

### Step 2: Generate the server key pair

Create the key files with restrictive permissions:

```bash
cd ~
umask 077
wg genkey | tee server_private.key | wg pubkey > server_public.key
```

Copy the keys into `/etc/wireguard`:

```bash
sudo install -d -m 700 /etc/wireguard
```

```bash
sudo install -m 600 server_private.key /etc/wireguard/server_private.key
sudo install -m 644 server_public.key /etc/wireguard/server_public.key
rm server_private.key server_public.key
```

Save the server public key for the client configuration:

```bash
sudo cat /etc/wireguard/server_public.key
```

Copy the server private key for the server configuration file:

```bash
sudo cat /etc/wireguard/server_private.key
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

In the Azure portal for the VM, add or confirm these inbound rules:

1. Allow WireGuard:
   source `Any`, destination port `51820`, protocol `UDP`, action `Allow`
2. Restrict SSH to the approved source IP ranges

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

### Step 7: Configure a client

Use a client configuration like this:

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

`AllowedIPs = 10.55.55.0/24` is split tunnel mode and routes only the VPN
subnet through WireGuard.

### Step 8: Validate the connection

From the client device:

```bash
ping 10.55.55.1
```

From the Ubuntu VM:

```bash
sudo wg show
```

The VM should show a recent handshake for the client peer after the tunnel
comes up.

### Step 9: Optional full-tunnel mode

To send all client traffic through the VM, change this line in the client
configuration:

```ini
AllowedIPs = 0.0.0.0/0
```

Keep IPv4 forwarding and the NAT rules enabled if full-tunnel mode is used.

## What You Just Set Up

WireGuard now provides private access to the Ubuntu VM and the services bound
to `10.55.55.1`. The rest of the application stack can stay off the public
internet and still be reachable from approved client devices.
