# WireGuard

## Purpose

Configure the Azure Ubuntu VM to act as a WireGuard VPN gateway so approved clients can securely access services on the VM over a private VPN subnet.

## Network Information

- WireGuard Subnet: `10.55.55.0/24`
- Server VPN IP: `10.55.55.1`
- WireGuard Port: `51820/UDP`
- Each client is assigned a unique VPN IP as `/32` (example: `10.55.55.2/32`)

Traffic path:

- The client sends encrypted UDP packets to the Azure VM public IP on port `51820`.
- The Azure VM decrypts packets and routes the decrypted traffic via `wg0` (VPN IP `10.55.55.1`).


## Server Setup (Ubuntu VM)

### 1) Install necessary libraries
- ssh into the virtual machine
- Install wireguard:

``` bash
sudo apt install wireguard-tools
```

### 2) Generate server keys

- Run these commands on the Ubuntu VM:

```bash
sudo umask 077
sudo wg genkey | sudo tee /etc/wireguard/server_private.key | wg pubkey | sudo tee /etc/wireguard/server_public.key
```

- View and copy the server private key (Paste in server config file wg0.conf):

```bash
sudo cat /etc/wireguard/server_private.key
```

### 3) Create server config: `/etc/wireguard/wg0.conf`

- Create/edit the file:

```bash
sudo nano /etc/wireguard/wg0.conf
```
- Paste and fill in values:

```ini
[Interface]
Address = 10.55.55.1/32
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY>

# NAT + forwarding (required if you want clients to route through the VM)
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -s 10.55.55.0/24 -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -s 10.55.55.0/24 -o eth0 -j MASQUERADE

# One [Peer] per client (repeat as needed)
[Peer]
# Example: Laptop client 1
PublicKey = <CLIENT_PUBLIC_KEY>
AllowedIPs = 10.55.55.0/24
# Example: Laptop client 2
[Peer]
PublicKey = <CLIENT_PUBLIC_KEY>
AllowedIPs = 10.55.55.0/24
```
Notes:

- `AllowedIPs` on the server binds a client public key to a single VPN IP (`/32`) or to a range (`/24`).
- Add one `[Peer]` block per client with a unique VPN IP or give them a large range they can be in.
- If you do not want the VM to NAT/route traffic for clients, you can remove `PostUp`/`PostDown`.


### 4) Enable IP forwarding (server)

```bash
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 5) Azure NSG inbound rules

1. Go to your virtual machine in the Azure web service
2. Locate Settings on left hand menu
3. Click on Networking
4. Add inbound security rule

- Rule to allow Wireguard
    * Source - Any
    * Source port ranges - `*`
    * Destination - Any
    * Service - Custom
    * Destination port ranges `51820`
    * Protocol - UDP
    * Action - Allow
    * Priority - 310
    * Name - AllowWireguard

- Rule to allow SSH (Should already be created)
    * Double click the SSH rule to edit
    * Source - IP Addresses
    * Source IP addresses/ CIDR range - Your company's allowed IP addresses
    * Destination - Any
    * Verify its protocal is TCP

### 6) Start the server

```bash
sudo wg-quick up wg0
sudo wg show
```

* Note: After adding Clients, you will need to restart Wireguard with 

```bash
sudo wq-quick down wg0
sudo wg-quick up wg0
```

## Client Setup (Windows)

### 1) Install WireGuard

Install WireGuard for Windows from the official installer.

### 2) Create a tunnel and generate keys

In the WireGuard app:

- Click **Add Tunnel**
- Select **Add empty tunnel**
- The app will generate a private key and public key

Copy the client public key and send it to the server administrator so it can be added as a `[Peer]` in `/etc/wireguard/wg0.conf`.

### 3) Configure the tunnel

Use a configuration like the following (fill in values):

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
Notes:

- Replace `10.55.55.2` with your assigned client VPN IP.
- `AllowedIPs = 10.55.55.0/24` is split-tunnel (only the VPN subnet routes through WireGuard).
- The VM Public IP can be found in the Azure Overview of the VM

Activate the tunnel in the WireGuard app.

### 4) Verify connection

```bash
ping 10.55.55.1
```

## Optional: Full-tunnel mode (route all traffic through Azure VM)

Client change:

```ini
AllowedIPs = 0.0.0.0/0
```
Server requirements:

- IP forwarding enabled
- NAT rules present in the server config (`PostUp`/`PostDown`)
- Azure NSG allows inbound UDP `51820`


## Client Setup (Linux)

### 1) Install WireGuard

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install wireguard
```

### 2) Generate client keys

```bash
umask 077
wg genkey | tee client_private.key | wg pubkey > client_public.key
```
Send `client_public.key` to the server administrator so it can be added as a `[Peer]` in `/etc/wireguard/wg0.conf`.

### 3) Create client config: `/etc/wireguard/wg0.conf`

```bash
sudo nano /etc/wireguard/wg0.conf
```
Paste and fill in values:

```ini
[Interface]
Address = 10.55.55.2/32
PrivateKey = <CLIENT_PRIVATE_KEY>
DNS = 8.8.8.8

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = <AZURE_PUBLIC_IP>:51820
AllowedIPs = 10.55.55.0/24
PersistentKeepalive = 25
```
Notes:

- Replace `10.55.55.2` with your assigned client VPN IP.
- `AllowedIPs = 10.55.55.0/24` is split-tunnel (only the VPN subnet routes through WireGuard).

### 4) Start and verify connection

```bash
sudo wg-quick up wg0
sudo wg show
ping 10.55.55.1
```
