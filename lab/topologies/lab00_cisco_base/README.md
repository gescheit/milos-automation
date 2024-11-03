## Lab00 Cisco Base

### Introduction:
In the Lab00, you will gain hands-on experience in deploying simple network configuration across an network infrastructure. This lab is designed to simulate a real-world scenario:
- mtu configuration
- description configuration

Author:
- [Vadim Volovik](https://github.com/vadvolo)

### Objectives:
- Understand the fundamental concepts of Annet

### Topology:

![Lab Topology](./images/topology.png)

### Preparation:

Before you start please put into `./scr/ios-7200` IOL image `c7200-jk9s-mz.124-13a`

### Run

**Step 1.**  
To start lab please navigate to `annetutils/labs` and run `make lab00`.

**Step 2.**  
Go to annet-container  
```
docker exec -u root -t -i netbox-docker-annet-1 /bin/bash
```

**Step 3.**  
Generate configuration for lab-r1, lab-r2, lab-r3

| Router | Command |
|:------:|:------:|
| lab-r1 | `python3 -m annet.annet gen lab-r1.nh.com` | 
| lab-r2 |`python3 -m annet.annet gen lab-r3.nh.com` | 
| lab-r3 |`python3 -m annet.annet gen lab-r3.nh.com` |

Output for `lab-r1`:
```
interface FastEthernet0/0
  description disconnected
  mtu 1500
interface FastEthernet0/1
  description disconnected
  mtu 1500
interface GigabitEthernet1/0
  description to_lab-r2.nh.com_GigabitEthernet1/0
  mtu 2000
interface GigabitEthernet2/0
  description disconnected
  mtu 1500
```

**Step 4.**  
Generate diff for lab-r1, lab-r2, lab-r3

| Router | Command |
|:------:|:------:|
| lab-r1 | `python3 -m annet.annet diff lab-r1.nh.com` | 
| lab-r2 |`python3 -m annet.annet diff lab-r3.nh.com` | 
| lab-r3 |`python3 -m annet.annet diff lab-r3.nh.com` |

Output for `lab-r1`:
```diff
  interface FastEthernet0/0
+   description disconnected
+   mtu 1500
  interface FastEthernet0/1
+   description disconnected
+   mtu 1500
  interface GigabitEthernet1/0
+   description to_lab-r2.nh.com_GigabitEthernet1/0
+   mtu 2000
  interface GigabitEthernet2/0
+   description disconnected
+   mtu 1500
```

**Step 5.**  
Generate patch for lab-r1, lab-r2, lab-r3

| Router | Command |
|:------:|:------:|
| lab-r1 | `python3 -m annet.annet patch lab-r1.nh.com` | 
| lab-r2 |`python3 -m annet.annet patch lab-r3.nh.com` | 
| lab-r3 |`python3 -m annet.annet patch lab-r3.nh.com` |

Output for `lab-r1`:
```diff
interface FastEthernet0/0
  description disconnected
  mtu 1500
  exit
interface FastEthernet0/1
  description disconnected
  mtu 1500
  exit
interface GigabitEthernet1/0
  description to_lab-r2.nh.com_GigabitEthernet1/0
  mtu 2000
  exit
interface GigabitEthernet2/0
  description disconnected
  mtu 1500
  exit
```

**Step 6.** 
Deploy configuration into for lab-r1, lab-r2, lab-r3

| Router | Command |
|:------:|:------:|
| lab-r1 | `python3 -m annet.annet deploy lab-r1.nh.com` | 
| lab-r2 |`python3 -m annet.annet deploy lab-r3.nh.com` | 
| lab-r3 |`python3 -m annet.annet deploy lab-r3.nh.com` |