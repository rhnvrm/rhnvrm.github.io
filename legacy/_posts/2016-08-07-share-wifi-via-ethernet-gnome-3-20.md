---
title: Share WiFi via Ethernet on Gnome 3.20
layout: post
---

There is a hidden method to share your WiFi over Ethernet in the latest Gnome. I stumbled upon this while trying to connect
my RaspberryPi 3B with my University's Internet. 

1. Type `nm-connection-editor` in your terminal.
2. Add a shared network connection by pressing the Add button. 
3. Choose Ethernet from the list and press Create.
4. Click IPv4 Settings in the left.
5. Choose `Shared to other computers` by clicking the Method drop-down menu. 
6. Enter a new name like `Shared WiFi LAN` as the Connection name at the top 
