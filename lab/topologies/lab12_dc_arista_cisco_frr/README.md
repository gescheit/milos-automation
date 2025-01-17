## Lab03. Multivendor lab

### Introduction

In this lab we will see how Annet manages software from several different vendors:

- Arista
- FRR
- Cisco

Author:

### Objectives

- To try out Annet in a multivendor environment

### Preparation

#### How to get Arista image

1. Go to https://www.arista.com/en/login
2. Log in or register at Arista.com
3. Go to https://www.arista.com/en/support/software-download
4. Download the `cEOS64-lab-4.33.0F.tar.xz`
5. Prepare docker image: `docker image import cEOS64-lab-4.33.0F.tar.xz arista-ceos:4.33.0F`

Now you're able to run Lab03.

### Topology

![Lab Topology](./images/topology.png)

### Lab Guide

**Step 1.**

If it was not done in one of the previous labs, build Netbox and Annet docker images:

```bash
cd annetutils/contribs/labs
make build
```

**Step 2.**

NOTE: Do not forget to put Cisco IOS image `c7200-jk9s-mz.124-13a.bin` into `../vm_images` directory and Arista image import.

Start the lab:

```bash
make lab12
```

NOTE: On Linux, `make` uses root privileges to execute the following command:

```bash
$(SUDO) find operational_configs -mindepth 1 -not -name '.gitkeep' -delete || true && \
```

which is required to clear operational configs if they exist.

**Step 3.**

Go to the Annet container:

```bash
docker exec -u root -t -i annet /bin/bash
```

Enable SSH on Cisco routers by executing the script:

```bash
for ip in 0 1; do netsshsetup -a 172.20.0.10$ip -b ios -l annet -p annet -P telnet -v cisco --ipdomain nh.com; done
```

**Step 4.**

Go to the Annet container:

```bash
docker exec -u root -t -i annet /bin/bash
```

Generate configuration for spine-1-1, spine-1-2, tor-1-1, tor-1-2, tor-1-3:

`annet gen spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

<details>
<summary>Arista Spine's configuration</summary>

```
hostname spine-1-1
interface Ethernet1
  description tor-1-1@GigabitEthernet1/0
  ip address 10.1.1.11/24
interface Ethernet2
  description tor-1-2@eth1
  ip address 10.1.2.11/24
interface Ethernet3
  description tor-1-3@GigabitEthernet1/0
  ip address 10.1.3.11/24
interface Management0
  ip address 172.20.0.110/24
ip community-list GSHUT permit GSHUT
ip community-list TOR_NETS permit 65000:1
route-map SPINE_IMPORT_TOR permit 10
  match community TOR_NETS
route-map SPINE_IMPORT_TOR deny 9999
route-map SPINE_EXPORT_TOR permit 10
  match community TOR_NETS
route-map SPINE_EXPORT_TOR deny 9999
router bgp 65201
  router-id 1.2.1.1
  neighbor TOR peer group
  neighbor TOR route-map SPINE_IMPORT_TOR in
  neighbor TOR route-map SPINE_EXPORT_TOR out
  neighbor TOR send-community
  neighbor 10.1.1.12 peer group TOR
  neighbor 10.1.1.12 remote-as 65111
  neighbor 10.1.2.12 peer group TOR
  neighbor 10.1.2.12 remote-as 65112
  neighbor 10.1.3.12 peer group TOR
  neighbor 10.1.3.12 remote-as 65113
  address-family ipv4
    neighbor TOR activate
```

</details>

<details>
<summary>FRR Spine's configuration</summary>

```
frr defaults datacenter
service integrated-vtysh-config

hostname spine-1-2
log file /var/log/frr/frr.log

interface eth0
 ip address 172.20.0.111/24
exit

interface eth1
 description tor-1-1.nh.com@GigabitEthernet2/0
 ip address 10.2.1.11/24
exit

interface eth2
 description tor-1-2.nh.com@eth2
 ip address 10.2.2.11/24
exit

interface eth3
 description tor-1-3.nh.com@GigabitEthernet2/0
 ip address 10.2.3.11/24
exit

router bgp 65201
 bgp router-id 1.2.1.2
 neighbor TOR peer-group
 neighbor 10.2.1.12 remote-as 65111
 neighbor 10.2.1.12 peer-group TOR
 neighbor 10.2.2.12 remote-as 65112
 neighbor 10.2.2.12 peer-group TOR
 neighbor 10.2.3.12 remote-as 65113
 neighbor 10.2.3.12 peer-group TOR
 address-family ipv4 unicast
  neighbor TOR route-map SPINE_IMPORT_TOR in
  neighbor TOR route-map SPINE_EXPORT_TOR out
 exit-address-family
exit

bgp community-list standard TOR_NETS seq 5 permit 65000:1
bgp community-list standard GSHUT seq 5 permit graceful-shutdown

route-map SPINE_IMPORT_TOR permit 10
 match community TOR_NETS
exit

route-map SPINE_IMPORT_TOR deny 9999
exit


route-map SPINE_EXPORT_TOR permit 10
 match community TOR_NETS
exit

route-map SPINE_EXPORT_TOR deny 9999
exit

line vty
```

</details>

<details>
<summary>Cisco Tor's configuration</summary>

```
hostname tor-1-1
ip bgp-community new-format
ip community-list standard GSHUT permit 65535:0
ip community-list standard TOR_NETS permit 65000:1
interface GigabitEthernet1/0
  no shutdown
  ip address 10.1.1.12 255.255.255.0
  description spine-1-1@Ethernet1
interface GigabitEthernet2/0
  no shutdown
  ip address 10.2.1.12 255.255.255.0
  description spine-1-2@eth1
interface FastEthernet0/0
  no shutdown
  ip address 172.20.0.100 255.255.255.0
interface Loopback0
  no shutdown
  ip address 10.0.0.1 255.255.255.255
interface FastEthernet0/1
  no shutdown
route-map TOR_IMPORT_SPINE permit 10
  match community GSHUT
  set local-preference 0
route-map TOR_IMPORT_SPINE permit 20
  set local-preference 100
route-map TOR_EXPORT_SPINE permit 10
  match community TOR_NETS
route-map TOR_EXPORT_SPINE deny 9999
route-map IMPORT_CONNECTED permit 10
  match interface Loopback0
  set community 65000:1
route-map IMPORT_CONNECTED deny 9999
router bgp 65111
  bgp router-id 1.1.1.1
  bgp log-neighbor-changes
  maximum-paths 16
  redistribute connected route-map IMPORT_CONNECTED
  neighbor SPINE peer-group
  neighbor SPINE route-map TOR_IMPORT_SPINE in
  neighbor SPINE route-map TOR_EXPORT_SPINE out
  neighbor SPINE soft-reconfiguration inbound
  neighbor SPINE send-community both
  neighbor 10.1.1.11 remote-as 65201
  neighbor 10.2.1.11 remote-as 65201
  neighbor 10.1.1.11 peer-group SPINE
  neighbor 10.2.1.11 peer-group SPINE
```

</details>

<details>
<summary>FRR Tor's configuration</summary>

```
frr defaults datacenter
service integrated-vtysh-config

hostname tor-1-2
log file /var/log/frr/frr.log

interface eth0
 ip address 172.20.0.113/24
exit

interface eth1
 description spine-1-1.nh.com@Ethernet2
 ip address 10.1.2.12/24
exit

interface eth2
 description spine-1-2.nh.com@eth2
 ip address 10.2.2.12/24
exit

interface eth3
exit

interface lo
 ip address 10.0.0.2/32
exit

router bgp 65112
 bgp router-id 1.1.1.2
 neighbor SPINE peer-group
 neighbor 10.1.2.11 remote-as 65201
 neighbor 10.1.2.11 peer-group SPINE
 neighbor 10.2.2.11 remote-as 65201
 neighbor 10.2.2.11 peer-group SPINE
 address-family ipv4 unicast
  redistribute connected route-map IMPORT_CONNECTED
  neighbor SPINE route-map TOR_IMPORT_SPINE in
  neighbor SPINE route-map TOR_EXPORT_SPINE out
  maximum-paths 16
 exit-address-family
exit

bgp community-list standard TOR_NETS seq 5 permit 65000:1
bgp community-list standard GSHUT seq 5 permit graceful-shutdown

route-map TOR_IMPORT_SPINE permit 10
 match community GSHUT
 set local-preference 0

route-map TOR_IMPORT_SPINE permit 20
 set local-preference 100

route-map TOR_EXPORT_SPINE permit 10
 match community TOR_NETS
exit

route-map TOR_EXPORT_SPINE deny 9999
exit

route-map IMPORT_CONNECTED permit 10
 match interface lo
 set community 65000:1
exit

route-map IMPORT_CONNECTED deny 9999
exit

line vty
```

</details>

Look at diff:

`annet diff spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

<details>
<summary>Arista Spine's Diff</summary>

```diff
+ hostname spine-1-1
- hostname spine
+ ip community-list GSHUT permit GSHUT
+ ip community-list TOR_NETS permit 65000:1
  interface Ethernet1
+   description tor-1-1@GigabitEthernet1/0
+   ip address 10.1.1.11/24
  interface Ethernet2
+   description tor-1-2@eth1
+   ip address 10.1.2.11/24
  interface Ethernet3
+   description tor-1-3@GigabitEthernet1/0
+   ip address 10.1.3.11/24
+ route-map SPINE_IMPORT_TOR permit 10
+   match community TOR_NETS
+ route-map SPINE_IMPORT_TOR deny 9999
+ route-map SPINE_EXPORT_TOR permit 10
+   match community TOR_NETS
+ route-map SPINE_EXPORT_TOR deny 9999
+ router bgp 65201
+   router-id 1.2.1.1
+   neighbor TOR peer group
+   neighbor TOR route-map SPINE_IMPORT_TOR in
+   neighbor TOR route-map SPINE_EXPORT_TOR out
+   neighbor TOR send-community
+   neighbor 10.1.1.12 peer group TOR
+   neighbor 10.1.1.12 remote-as 65111
+   neighbor 10.1.2.12 peer group TOR
+   neighbor 10.1.2.12 remote-as 65112
+   neighbor 10.1.3.12 peer group TOR
+   neighbor 10.1.3.12 remote-as 65113
+   address-family ipv4
+     neighbor TOR activate
```

</details>

<details>
<summary>FRR Spine's Diff</summary>

```diff
---
+++
@@ -1,7 +1,7 @@
 frr defaults datacenter
 service integrated-vtysh-config

-hostname frr-r1
+hostname spine-1-2
 log file /var/log/frr/frr.log

 interface eth0
@@ -9,15 +9,51 @@
 exit

 interface eth1
- no ip address
+ description tor-1-1.nh.com@GigabitEthernet2/0
+ ip address 10.2.1.11/24
 exit

 interface eth2
- no ip address
+ description tor-1-2.nh.com@eth2
+ ip address 10.2.2.11/24
 exit

 interface eth3
- no ip address
+ description tor-1-3.nh.com@GigabitEthernet2/0
+ ip address 10.2.3.11/24
+exit
+
+router bgp 65201
+ bgp router-id 1.2.1.2
+ neighbor TOR peer-group
+ neighbor 10.2.1.12 remote-as 65111
+ neighbor 10.2.1.12 peer-group TOR
+ neighbor 10.2.2.12 remote-as 65112
+ neighbor 10.2.2.12 peer-group TOR
+ neighbor 10.2.3.12 remote-as 65113
+ neighbor 10.2.3.12 peer-group TOR
+ address-family ipv4 unicast
+  neighbor TOR route-map SPINE_IMPORT_TOR in
+  neighbor TOR route-map SPINE_EXPORT_TOR out
+ exit-address-family
+exit
+
+bgp community-list standard TOR_NETS seq 5 permit 65000:1
+bgp community-list standard GSHUT seq 5 permit graceful-shutdown
+
+route-map SPINE_IMPORT_TOR permit 10
+ match community TOR_NETS
+exit
+
+route-map SPINE_IMPORT_TOR deny 9999
+exit
+
+
+route-map SPINE_EXPORT_TOR permit 10
+ match community TOR_NETS
+exit
+
+route-map SPINE_EXPORT_TOR deny 9999
 exit

 line vty
```

</details>

<details>
<summary>Cisco Tor's Diff</summary>

```diff
+ hostname tor-1-1
- hostname lab-r1
+ ip bgp-community new-format
+ interface Loopback0
+   no shutdown
+   ip address 10.0.0.1 255.255.255.255
+ route-map TOR_IMPORT_SPINE permit 10
+   match community GSHUT
+   set local-preference 0
+ route-map TOR_IMPORT_SPINE permit 20
+   set local-preference 100
+ route-map TOR_EXPORT_SPINE permit 10
+   match community TOR_NETS
+ route-map TOR_EXPORT_SPINE deny 9999
+ route-map IMPORT_CONNECTED permit 10
+   match interface Loopback0
+   set community 65000:1
+ route-map IMPORT_CONNECTED deny 9999
+ ip community-list standard GSHUT permit 65535:0
+ ip community-list standard TOR_NETS permit 65000:1
+ router bgp 65111
+   bgp router-id 1.1.1.1
+   bgp log-neighbor-changes
+   maximum-paths 16
+   redistribute connected route-map IMPORT_CONNECTED
+   neighbor SPINE peer-group
+   neighbor SPINE route-map TOR_IMPORT_SPINE in
+   neighbor SPINE route-map TOR_EXPORT_SPINE out
+   neighbor SPINE soft-reconfiguration inbound
+   neighbor SPINE send-community both
+   neighbor 10.1.1.11 remote-as 65201
+   neighbor 10.2.1.11 remote-as 65201
+   neighbor 10.1.1.11 peer-group SPINE
+   neighbor 10.2.1.11 peer-group SPINE
  interface GigabitEthernet1/0
-   shutdown
+   ip address 10.1.1.12 255.255.255.0
+   description spine-1-1@Ethernet1
  interface GigabitEthernet2/0
-   shutdown
+   ip address 10.2.1.12 255.255.255.0
+   description spine-1-2@eth1
  interface FastEthernet0/1
-   shutdown
```

</details>

<details>
<summary>FRR Tor's Diff</summary>

```diff
---
+++
@@ -1,7 +1,7 @@
 frr defaults datacenter
 service integrated-vtysh-config

-hostname frr-r1
+hostname tor-1-2
 log file /var/log/frr/frr.log

 interface eth0
@@ -9,15 +9,60 @@
 exit

 interface eth1
- no ip address
+ description spine-1-1.nh.com@Ethernet2
+ ip address 10.1.2.12/24
 exit

 interface eth2
- no ip address
+ description spine-1-2.nh.com@eth2
+ ip address 10.2.2.12/24
 exit

 interface eth3
- no ip address
+exit
+
+interface lo
+ ip address 10.0.0.2/32
+exit
+
+router bgp 65112
+ bgp router-id 1.1.1.2
+ neighbor SPINE peer-group
+ neighbor 10.1.2.11 remote-as 65201
+ neighbor 10.1.2.11 peer-group SPINE
+ neighbor 10.2.2.11 remote-as 65201
+ neighbor 10.2.2.11 peer-group SPINE
+ address-family ipv4 unicast
+  redistribute connected route-map IMPORT_CONNECTED
+  neighbor SPINE route-map TOR_IMPORT_SPINE in
+  neighbor SPINE route-map TOR_EXPORT_SPINE out
+  maximum-paths 16
+ exit-address-family
+exit
+
+bgp community-list standard TOR_NETS seq 5 permit 65000:1
+bgp community-list standard GSHUT seq 5 permit graceful-shutdown
+
+route-map TOR_IMPORT_SPINE permit 10
+ match community GSHUT
+ set local-preference 0
+
+route-map TOR_IMPORT_SPINE permit 20
+ set local-preference 100
+
+route-map TOR_EXPORT_SPINE permit 10
+ match community TOR_NETS
+exit
+
+route-map TOR_EXPORT_SPINE deny 9999
+exit
+
+route-map IMPORT_CONNECTED permit 10
+ match interface lo
+ set community 65000:1
+exit
+
+route-map IMPORT_CONNECTED deny 9999
 exit

 line vty
```

</details>

Look at patch:

`annet patch spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

<details>
<summary>Arista Spine's Patch</summary>

```
no hostname spine
hostname spine-1-1
interface Ethernet1
  description tor-1-1@GigabitEthernet1/0
  ip address 10.1.1.11/24
  exit
interface Ethernet2
  description tor-1-2@eth1
  ip address 10.1.2.11/24
  exit
interface Ethernet3
  description tor-1-3@GigabitEthernet1/0
  ip address 10.1.3.11/24
  exit
ip community-list GSHUT permit GSHUT
ip community-list TOR_NETS permit 65000:1
route-map SPINE_IMPORT_TOR permit 10
  match community TOR_NETS
  exit
route-map SPINE_IMPORT_TOR deny 9999
  exit
route-map SPINE_EXPORT_TOR permit 10
  match community TOR_NETS
  exit
route-map SPINE_EXPORT_TOR deny 9999
  exit
router bgp 65201
  router-id 1.2.1.1
  neighbor TOR peer group
  neighbor TOR route-map SPINE_IMPORT_TOR in
  neighbor TOR route-map SPINE_EXPORT_TOR out
  neighbor TOR send-community
  neighbor 10.1.1.12 peer group TOR
  neighbor 10.1.1.12 remote-as 65111
  neighbor 10.1.2.12 peer group TOR
  neighbor 10.1.2.12 remote-as 65112
  neighbor 10.1.3.12 peer group TOR
  neighbor 10.1.3.12 remote-as 65113
  address-family ipv4
    neighbor TOR activate
    exit
  exit
```

</details>

<details>
<summary>FRR Spine's Patch</summary>

```
frr defaults datacenter
service integrated-vtysh-config

hostname spine-1-2
log file /var/log/frr/frr.log

interface eth0
 ip address 172.20.0.111/24
exit

interface eth1
 description tor-1-1.nh.com@GigabitEthernet2/0
 ip address 10.2.1.11/24
exit

interface eth2
 description tor-1-2.nh.com@eth2
 ip address 10.2.2.11/24
exit

interface eth3
 description tor-1-3.nh.com@GigabitEthernet2/0
 ip address 10.2.3.11/24
exit

router bgp 65201
 bgp router-id 1.2.1.2
 neighbor TOR peer-group
 neighbor 10.2.1.12 remote-as 65111
 neighbor 10.2.1.12 peer-group TOR
 neighbor 10.2.2.12 remote-as 65112
 neighbor 10.2.2.12 peer-group TOR
 neighbor 10.2.3.12 remote-as 65113
 neighbor 10.2.3.12 peer-group TOR
 address-family ipv4 unicast
  neighbor TOR route-map SPINE_IMPORT_TOR in
  neighbor TOR route-map SPINE_EXPORT_TOR out
 exit-address-family
exit

bgp community-list standard TOR_NETS seq 5 permit 65000:1
bgp community-list standard GSHUT seq 5 permit graceful-shutdown

route-map SPINE_IMPORT_TOR permit 10
 match community TOR_NETS
exit

route-map SPINE_IMPORT_TOR deny 9999
exit


route-map SPINE_EXPORT_TOR permit 10
 match community TOR_NETS
exit

route-map SPINE_EXPORT_TOR deny 9999
exit

line vty
```

</details>

<details>
<summary>Cisco Tor's Patch</summary>

```
no hostname lab-r1
hostname tor-1-1
ip community-list standard GSHUT permit 65535:0
ip community-list standard TOR_NETS permit 65000:1
ip bgp-community new-format
interface GigabitEthernet1/0
  no shutdown
  ip address 10.1.1.12 255.255.255.0
  description spine-1-1@Ethernet1
  exit
interface GigabitEthernet2/0
  no shutdown
  ip address 10.2.1.12 255.255.255.0
  description spine-1-2@eth1
  exit
interface FastEthernet0/1
  no shutdown
  exit
interface Loopback0
  ip address 10.0.0.1 255.255.255.255
  no shutdown
  exit
route-map TOR_IMPORT_SPINE permit 10
  match community GSHUT
  set local-preference 0
  exit
route-map TOR_IMPORT_SPINE permit 20
  set local-preference 100
  exit
route-map TOR_EXPORT_SPINE permit 10
  match community TOR_NETS
  exit
route-map TOR_EXPORT_SPINE deny 9999
route-map IMPORT_CONNECTED permit 10
  match interface Loopback0
  set community 65000:1
  exit
route-map IMPORT_CONNECTED deny 9999
router bgp 65111
  bgp router-id 1.1.1.1
  bgp log-neighbor-changes
  maximum-paths 16
  redistribute connected route-map IMPORT_CONNECTED
  neighbor SPINE peer-group
  neighbor SPINE route-map TOR_IMPORT_SPINE in
  neighbor SPINE route-map TOR_EXPORT_SPINE out
  neighbor SPINE soft-reconfiguration inbound
  neighbor SPINE send-community both
  neighbor 10.1.1.11 remote-as 65201
  neighbor 10.2.1.11 remote-as 65201
  neighbor 10.1.1.11 peer-group SPINE
  neighbor 10.2.1.11 peer-group SPINE
  exit
```

</details>

<details>
<summary>FRR Tor's Patch</summary>

```
frr defaults datacenter
service integrated-vtysh-config

hostname tor-1-2
log file /var/log/frr/frr.log

interface eth0
 ip address 172.20.0.113/24
exit

interface eth1
 description spine-1-1.nh.com@Ethernet2
 ip address 10.1.2.12/24
exit

interface eth2
 description spine-1-2.nh.com@eth2
 ip address 10.2.2.12/24
exit

interface eth3
exit

interface lo
 ip address 10.0.0.2/32
exit

router bgp 65112
 bgp router-id 1.1.1.2
 neighbor SPINE peer-group
 neighbor 10.1.2.11 remote-as 65201
 neighbor 10.1.2.11 peer-group SPINE
 neighbor 10.2.2.11 remote-as 65201
 neighbor 10.2.2.11 peer-group SPINE
 address-family ipv4 unicast
  redistribute connected route-map IMPORT_CONNECTED
  neighbor SPINE route-map TOR_IMPORT_SPINE in
  neighbor SPINE route-map TOR_EXPORT_SPINE out
  maximum-paths 16
 exit-address-family
exit

bgp community-list standard TOR_NETS seq 5 permit 65000:1
bgp community-list standard GSHUT seq 5 permit graceful-shutdown

route-map TOR_IMPORT_SPINE permit 10
 match community GSHUT
 set local-preference 0

route-map TOR_IMPORT_SPINE permit 20
 set local-preference 100

route-map TOR_EXPORT_SPINE permit 10
 match community TOR_NETS
exit

route-map TOR_EXPORT_SPINE deny 9999
exit

route-map IMPORT_CONNECTED permit 10
 match interface lo
 set community 65000:1
exit

route-map IMPORT_CONNECTED deny 9999
exit

line vty
```

</details>

Deploy it:

`annet deploy spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

**Step 5.**

Break a connection and check what happens.

Go to [Netbox](http://localhost:8000/), use annet:annet as login:password. Delete the connection between tor-1-2.nh.com and spine-1-1.nh.com.

Look at diff:

`annet diff spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

<details>
<summary>spine-1-1 Diff</summary>

```
  interface Ethernet2
-   description tor-1-2@eth1
-   ip address 10.1.2.11/24
  router bgp 65201
-   neighbor 10.1.2.12 peer group TOR
-   neighbor 10.1.2.12 remote-as 65112
```

</details>

<details>
<summary>tor-1-2 Diff</summary>

```
---
+++
@@ -9,8 +9,6 @@
 exit

 interface eth1
- description spine-1-1.nh.com@Ethernet2
- ip address 10.1.2.12/24
 exit

 interface eth2
@@ -28,8 +26,6 @@
 router bgp 65112
  bgp router-id 1.1.1.2
  neighbor SPINE peer-group
- neighbor 10.1.2.11 remote-as 65201
- neighbor 10.1.2.11 peer-group SPINE
  neighbor 10.2.2.11 remote-as 65201
  neighbor 10.2.2.11 peer-group SPINE
  address-family ipv4 unicast
```

</details>

Look at patch:

`annet patch spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

<details>
<summary>spine-1-1 Patch</summary>

```
interface Ethernet2
  no description tor-1-2@eth1
  no ip address 10.1.2.11/24
  exit
router bgp 65201
  no neighbor 10.1.2.12 peer group TOR
  no neighbor 10.1.2.12 remote-as 65112
  exit
```

</details>

<details>
<summary>tor-1-2 Patch</summary>

```
frr defaults datacenter
service integrated-vtysh-config

hostname tor-1-2
log file /var/log/frr/frr.log

interface eth0
 ip address 172.20.0.113/24
exit

interface eth1
exit

interface eth2
 description spine-1-2.nh.com@eth2
 ip address 10.2.2.12/24
exit

interface eth3
exit

interface lo
 ip address 10.0.0.2/32
exit

router bgp 65112
 bgp router-id 1.1.1.2
 neighbor SPINE peer-group
 neighbor 10.2.2.11 remote-as 65201
 neighbor 10.2.2.11 peer-group SPINE
 address-family ipv4 unicast
  redistribute connected route-map IMPORT_CONNECTED
  neighbor SPINE route-map TOR_IMPORT_SPINE in
  neighbor SPINE route-map TOR_EXPORT_SPINE out
  maximum-paths 16
 exit-address-family
exit

bgp community-list standard TOR_NETS seq 5 permit 65000:1
bgp community-list standard GSHUT seq 5 permit graceful-shutdown

route-map TOR_IMPORT_SPINE permit 10
 match community GSHUT
 set local-preference 0

route-map TOR_IMPORT_SPINE permit 20
 set local-preference 100

route-map TOR_EXPORT_SPINE permit 10
 match community TOR_NETS
exit

route-map TOR_EXPORT_SPINE deny 9999
exit

route-map IMPORT_CONNECTED permit 10
 match interface lo
 set community 65000:1
exit

route-map IMPORT_CONNECTED deny 9999
exit

line vty
```

</details>

Deploy it:

`annet deploy spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

Restore the connection and repeat the actions.

**Step 6.**

Drain traffic from one of the spines.

Go to [Netbox](http://localhost:8000/), use annet:annet as login:password. Assign spine-1-1.nh.com or spine-1-2.nh.com tag "maintenance".

Look at diff:

`annet diff spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

<details>
<summary>spine-1-1 Diff</summary>

```
  route-map SPINE_EXPORT_TOR permit 10
+   set community 65535:0 additive
```

</details>

<details>
<summary>FRR Spine's Diff</summary>

```
---
+++
@@ -51,6 +51,7 @@

 route-map SPINE_EXPORT_TOR permit 10
  match community TOR_NETS
+ set community 65535:0 additive
 exit

 route-map SPINE_EXPORT_TOR deny 9999
```

</details>

Look at patch:

`annet patch spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

<details>
<summary>spine-1-1 Patch</summary>

```
route-map SPINE_EXPORT_TOR permit 10
  set community 65535:0 additive
  exit
```

</details>

<details>
<summary>FRR Spine's Patch</summary>

```
frr defaults datacenter
service integrated-vtysh-config

hostname spine-1-2
log file /var/log/frr/frr.log

interface eth0
 ip address 172.20.0.111/24
exit

interface eth1
 description tor-1-1.nh.com@GigabitEthernet2/0
 ip address 10.2.1.11/24
exit

interface eth2
 description tor-1-2.nh.com@eth2
 ip address 10.2.2.11/24
exit

interface eth3
 description tor-1-3.nh.com@GigabitEthernet2/0
 ip address 10.2.3.11/24
exit

router bgp 65201
 bgp router-id 1.2.1.2
 neighbor TOR peer-group
 neighbor 10.2.1.12 remote-as 65111
 neighbor 10.2.1.12 peer-group TOR
 neighbor 10.2.2.12 remote-as 65112
 neighbor 10.2.2.12 peer-group TOR
 neighbor 10.2.3.12 remote-as 65113
 neighbor 10.2.3.12 peer-group TOR
 address-family ipv4 unicast
  neighbor TOR route-map SPINE_IMPORT_TOR in
  neighbor TOR route-map SPINE_EXPORT_TOR out
 exit-address-family
exit

bgp community-list standard TOR_NETS seq 5 permit 65000:1
bgp community-list standard GSHUT seq 5 permit graceful-shutdown

route-map SPINE_IMPORT_TOR permit 10
 match community TOR_NETS
exit

route-map SPINE_IMPORT_TOR deny 9999
exit


route-map SPINE_EXPORT_TOR permit 10
 match community TOR_NETS
 set community 65535:0 additive
exit

route-map SPINE_EXPORT_TOR deny 9999
exit

line vty
```

</details>

Deploy it:

`annet deploy spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

Remove the tag and repeat the actions.

**Step 7.**

After finishing the lab, stop it:

```bash
make services_stop
```
