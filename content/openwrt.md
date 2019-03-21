Title: Configuring OpenWRT on a Linksys WRT32X
Date: 2019-03-05 21:20
Category: Guide
Summary:

A recent update of [OpenWrt](https://openwrt.org/) on my [TP-Link TL-WR1043ND](https://openwrt.org/toh/tp-link/tl-wr1043nd) proved a bit too much for it.
[OpenWrt 18.06.2](https://openwrt.org/releases/18.06/notes-18.06.2) installed ok but free space was lacking and opkg didn't work well.

Setting up a build environment and building a custom image would take a bit of time, and I noticed the Linksys WRT32X was going relatively cheap in the UK.

So I bought one, meaning I could start using that and build the image for the TP-Link at my leisure another time.

[![Alt text](/images/wrt32x/small/wrt32x_small.jpg)](images/wrt32x/wrt32x.jpg)

The stock firmware lasted about 5 minutes before I decided to flash [OpenWrt](https://openwrt.org/), so I decided to document my setup.

Some of the initial basic configuration (setting up the main wireless network) was done via luci and then settings were checked and adjusted in the uci config files.
Below is some of the extra configuration/tweaks I did.

## Wireless
* Reduce transmit power on wireless networks to 15dBm

`/etc/config/wireless`
```
config wifi-device '???'
	option txpower '15'
```
## DHCP
* Main dhcp options can be left as default:

`/etc/config/dhcp`
```
config dnsmasq
	option domainneeded '1'
	option localise_queries '1'
	option rebind_protection '1'
	option rebind_localhost '1'
	option local '/lan/'
	option domain 'lan'
	option expandhosts '1'
	option authoritative '1'
	option readethers '1'
	option leasefile '/tmp/dhcp.leases'
	option resolvfile '/tmp/resolv.conf.auto'
	option nonwildcard '1'
	option localservice '1'
```
* Dhcp pools - remove ra and dhcpv6 options, dhcp options to return pi-hole as DNS server and openwrt as secondary

`/etc/config/dhcp`
```
config dhcp 'lan'
	option interface 'lan'
	option start '100'
	option limit '150'
	option leasetime '12h'
	list dhcp_option '6,192.168.1.2,192.168.1.1'
```
* Configure static leases

`/etc/config/dhcp`
```
config host
	option name 'mypc'
	option dns '1'
	option mac '00:11:22:33:44:55'
```
## DNS
* Upstream DNS Servers - Use cloudfare - 1.1.1.1, 1.0.0.1

`/etc/config/network`
```
config interface 'wan'
	option peerdns '0'
  	option dns '1.1.1.1 1.0.0.1'
```
## Guest WiFi
`/etc/config/wireless`
```
config wifi-iface
	option device '???'
	option mode 'ap'
	option network 'guest'
	option ssid 'Guest'
	option encryption 'psk2'
	option key 'GuestWifiKey'
	option isolate '1'
```  
`/etc/config/network`
```
config interface 'guest'
	option proto 'static'
	option ipaddr '192.168.2.1'
	option netmask '255.255.255.0'
```
* Guest Wifi use OpenDNS Family shield for DNS - 208.67.222.123, 208.67.220.123
  
`/etc/config/dhcp`
```
config dhcp 'guest'
	option interface 'guest'
    	option start '100'
    	option limit '150'
    	option leasetime '1h'
    	list dhcp_option '6,208.67.222.123,208.67.220.123'
```
* Setup firewall zone, forwardings and allow DHCP requests. Deny access to the Cable Modem IP
  
`/etc/config/firewall`
```
config zone                                     
	option name 'guest'                 
	option network 'guest'
	option input 'REJECT'        
	option forward 'REJECT'             
	option output 'ACCEPT'              
       
config forwarding                               
	option src 'guest'                  
	option dest 'wan'
       
# Allow DHCP Guest -> Router
# DHCP communication uses UDP ports 67-68
config rule
	option name 'Allow-Guest-DHCP'
	option src 'guest'
	option dest_port '67-68'
	option proto 'udp'
	option target 'ACCEPT'
    
# Don't allow access to the cable modem
config rule
	option name 'Deny-Guest-Cable-Modem'
	option src 'guest'
	option dest 'wan'
	option dest_ip '192.168.100.1'
 	option family 'ipv4'
	option proto 'all'
	option target 'REJECT'
```
## Dynamic DNS 
* Install ca-certificates so https works, password is the update.php key

`/etc/config/ddns`
```
config service 'myddns_ipv4'
	option interface 'wan'
	option ip_source 'network'
	option ip_network 'wan'
	option service_name 'afraid.org-keyauth'
	option enabled '1'
	option lookup_host '???'
	option password '???
	option use_https '1'
```
## VPN
* Install Easy-RSA
```
opkg update
opkg install openvpn-easy-rsa
```
* OpenWRT has a good guide on creating the key pairs so will use this. 
* **EASYRSA_PKI** is the **PKI** directory, **EASYRSA_REQ_CN** is the Certificate Authority Common Name. 
* **vpn-server** is the servers common name and **vpn-client1** is the client's common name.
```
export EASYRSA_PKI="/etc/easy-rsa/pki"
export EASYRSA_REQ_CN="vpnca"
```
* Remove and re-initialize the PKI directory
```
easyrsa --batch init-pki
```
* Generate DH parameters
```
easyrsa --batch gen-dh
```
* Create a new CA
```
easyrsa --batch build-ca nopass
```
* Generate a keypair and sign locally for vpn-server
```
easyrsa --batch build-server-full vpn-server nopass
```
* Generate a keypair and sign locally for vpn-client1
```
easyrsa --batch build-client-full vpn-client1 nopass
```
* Install OpenVPN
```
opkg update
opkg install openvpn-openssl
```
* Generate TLS PSL
```
EASYRSA_PKI="/etc/easy-rsa/pki"
openvpn --genkey --secret "${EASYRSA_PKI}/tc.key"
```
`/etc/config/openvpn`
```
config openvpn 'vpn'
	option enabled '1'
	option verb '3'
	option user 'nobody'
	option group 'nogroup'
	option dev 'tun'
	option port '1194'
	option proto 'udp4'
	option server '10.8.0.0 255.255.255.0'
	option topology 'subnet'
	option persist_tun '1'
	option persist_key '1'
	list push 'route 192.168.1.0 255.255.255.0'
	list push 'dhcp-option DNS 192.168.1.2'
	list push 'dhcp-option DNS 192.168.1.1'
	list push 'redirect-gateway def1'
	list push 'persist-tun'
	list push 'persist-key'
	option keepalive '10 120'
	option ca '/etc/openvpn/ca.crt'
	option cert '/etc/openvpn/vpn-server.crt'
	option key '/etc/openvpn/vpn-server.key'
	option dh '/etc/openvpn/dh.pem'
	option tls_crypt '/etc/openvpn/tc.key'
	option cipher 'AES-256-CBC'
	option fragment '1400'
```
`/etc/config/firewall`
```
config rule
        option name 'Allow-OpenVPN-Inbound'
        option target 'ACCEPT'
        option src 'wan'
        option proto 'udp'
        option dest_port '1194'

config zone 'vpn'
        option name 'vpn'
        option network 'vpn'
        option input 'ACCEPT'
        option forward 'REJECT'
        option output 'ACCEPT'
        option masq '1'

config forwarding 'vpn_forwarding_lan_in'
        option src 'vpn'
        option dest 'lan'

config forwarding 'vpn_forwarding_lan_out'
        option src 'lan'
        option dest 'vpn'

config forwarding 'vpn_forwarding_wan'
        option src 'vpn'
        option dest 'wan'
```

## Collectd

* Enabled plugins cpu,memory,network,thermal,uptime
* Added network plugin settings

`/etc/config/luci_statistics`

```
config statistics 'collectd_network'
	option enable '1'
	option Forward '0'

config collectd_network_server
        option port '25826'
        option host '192.168.1.2'
```
## Misc

* Turn off "**Use builtin IPv6-management**" for all interfaces
	
* Turn off ipv6 support for current session and preserve change across reboots
```
sysctl -w net.ipv6.conf.all.disable_ipv6=1
sysctl -w net.ipv6.conf.default.disable_ipv6 = 1
```
`/etc/sysctl.conf`

```
net.ipv6.conf.all.disable_ipv6=1
net.ipv6.conf.default.disable_ipv6 = 1
```
* Configure subdomains

`/etc/dnsmasq.conf.domains`
```
domain=wired.lan,192.168.1.0/24,local
domain=guest.lan,192.168.2.0/24,local
```
* Add this as an extra dnsmasq config file and add it to the list of files included in config backups (courtesy of [https://www.middling.uk/blog/2015/03/customising-openwrt-to-my-needs/](https://www.middling.uk/blog/2015/03/customising-openwrt-to-my-needs/))
```
echo "conf-file=/etc/dnsmasq.conf.domains" >> /etc/dnsmasq.conf
echo "/etc/dnsmasq.conf.domains" >> /etc/sysupgrade.conf
```