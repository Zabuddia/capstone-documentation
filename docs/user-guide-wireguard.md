# WireGuard User Guide

## Overview

WireGuard is the VPN used to connect your computer to the private server that hosts the AI tools (OpenWebUI, RAG Website, Cline). All of those services are only reachable over the VPN — they are not exposed to the public internet. You need WireGuard running before you can access any of them.

This guide covers everything a new user needs to do to get connected. The server-side setup is handled by your administrator.

---

## What You Need from Your Administrator

Before you can connect, your administrator needs to add your device to the VPN server. To do that, they need your **public key**, which WireGuard generates for you (covered in Step 2 below).

Your administrator will give you:

- Your assigned **VPN IP address** (e.g. `10.55.55.2`)
- The server's **public key**
- The server's **public IP address**

You will need all three to complete your tunnel configuration.

---

## Step 1: Install WireGuard

Download and install WireGuard for Windows from the official installer:

[wireguard.com/install](https://www.wireguard.com/install/)

Run the installer and open the WireGuard app when it finishes.

---

## Step 2: Create a Tunnel and Get Your Public Key

1. In the WireGuard app, click **Add Tunnel** → **Add empty tunnel**.
2. WireGuard automatically generates a **private key** (already filled in) and a **public key** shown at the top of the editor.
3. Copy your **public key** and send it to your administrator.

!!! warning "Keep your private key private"
    Never share the private key. Only share the public key with your administrator.

!!! note "Wait before activating"
    Do not activate the tunnel yet. Wait until your administrator confirms your public key has been added to the server.

---

## Step 3: Configure the Tunnel

Once your administrator confirms you have been added, replace the contents of the tunnel editor with the following and fill in the three placeholders:

```ini
[Interface]
PrivateKey = <YOUR_PRIVATE_KEY>
Address = <YOUR_VPN_IP>/32
DNS = 8.8.8.8

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = <SERVER_PUBLIC_IP>:51820
AllowedIPs = 10.55.55.0/24
PersistentKeepalive = 25
```

- `<YOUR_PRIVATE_KEY>` — already present in the editor from Step 2, leave it as-is
- `<YOUR_VPN_IP>` — the IP address your administrator assigned to you (e.g. `10.55.55.2`)
- `<SERVER_PUBLIC_KEY>` — provided by your administrator
- `<SERVER_PUBLIC_IP>` — provided by your administrator

Click **Save**.

---

## Step 4: Activate the Tunnel

Click **Activate** in the WireGuard app. The status should change to **Active**.

To verify the connection, open a terminal and ping the VPN gateway:

```
ping 10.55.55.1
```

If you get replies, you are connected. You can now open a browser and access the internal services.

---

## Connecting and Disconnecting

WireGuard does not need to run all the time. You can toggle it on and off as needed:

- **To connect:** Open WireGuard and click **Activate** on your tunnel.
- **To disconnect:** Open WireGuard and click **Deactivate**.

You must have the tunnel **Active** to reach any of the internal services.

---

## Internal Service URLs

Once WireGuard is active, open these URLs in your browser:

| Service | URL |
|---|---|
| OpenWebUI (AI chat) | `http://10.55.55.1:3000` |
| RAG Website (index manager) | `http://10.55.55.1:7000` |
| LiteLLM | `http://10.55.55.1:4000` |
| MCP Docs | `http://10.55.55.1:8001/docs` |

---

## Troubleshooting

**The tunnel activates but I can't reach the services.**
Make sure the tunnel status shows **Active**, then try pinging `10.55.55.1` in a terminal. If the ping fails, your administrator may need to restart the VPN server or check your peer entry.

**WireGuard says "Activation failed".**
Double-check that the `PublicKey`, `Endpoint`, and `Address` values in your tunnel configuration exactly match what your administrator provided.

**I got a new computer and need to reconnect.**
You will need to repeat Steps 1–4 on the new machine. WireGuard generates a new key pair per installation, so your administrator will need your new public key before you can connect.
