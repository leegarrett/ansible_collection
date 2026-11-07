# Collection layout

Proposed grouping, by what someone would install together:

| Collection                | Roles                                                                                                                                | Playbooks     | Depends on           |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------|----------------------|
| leegarrett.kubernetes     | apt_kubernetes, cilium_cli, containerd, helm, helmfile, kube_user, kubectl, kubernetes                                               | wipe          |                      |
| leegarrett.elastic        | apt_elastico, elasticsearch, kibana, logstash                                                                                        |               |                      |
| leegarrett.mail           | apt_rspamd, dovecot, nullmailer, postfix, rspamd                                                                                     |               | leegarrett.databases |
| leegarrett.databases      | autopostgresqlbackup, postgresql, redis                                                                                              |               |                      |
| leegarrett.web            | apache2, apache2_php_fpm, apache2_wsgi, apt_collaboraoffice, certbot, haproxy, mediawiki, nextcloud, php_fpm, static_tls             |               | leegarrett.databases |
| leegarrett.graphite       | graphite_carbon, graphite_web                                                                                                        |               | leegarrett.web       |
| leegarrett.network        | dnsmasq, hostapd, iodined, network_manager, openvpn, pppoe, systemd_link, tor, unbound, wireguard_server                             | migrate_to_nm |                      |
| leegarrett.security       | firewalld, server_hardening, shorewall, sshd, sshguard                                                                               |               |                      |
| leegarrett.debian_dev     | apt_cacher_ng, apt_pyxian, git_buildpackage, mini_dinstall, pyxian, sbuild                                                           |               |                      |
| leegarrett.debian         | apt_debian, borgmatic, locales, rsyslog, timesync                                                                                    | upgrade       |                      |
| leegarrett.desktop        | firefox, flatpak, gnome, kodi, nextcloud_desktop, noise_suppression, snapd, vscode, vscode_continue_langdock                         |               |                      |
| leegarrett.hardware       | chameleon_mini, fwupd, hp_color_laserjet_mfp_m277dw, logitech_g502, physical_host, proxmark3, raid_controller, smartd, thinkfan, zfs |               |                      |
| leegarrett.virtualization | apt_docker, docker, qemu_guest, qemu_host                                                                                            |               |                      |
| leegarrett.games          | ark, mumble, retroarch, steamcmd                                                                                                     |               |                      |
| leegarrett.windows        | apply_win_updates, bootstrap_windows, win_firefox, win_gaming_overlay, winfsp                                                        | bootstrap     |                      |
| leegarrett.services       | ejabberd, home_assistant, samba, vllm                                                                                                |               |                      |

`leegarrett.services` is a catch-all and may be split up later.
