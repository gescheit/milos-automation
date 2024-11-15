from annet.generators import BaseGenerator
from annet.storage import Storage

from . import bgp, description, hostname, ip_addresses, rpl, shutdown, entire_frr


def get_generators(store: Storage) -> list[BaseGenerator]:
    return [
        bgp.Bgp(store),
        description.Description(store),
        entire_frr.Frr(store),
        hostname.Hostname(store),
        ip_addresses.IpAddresses(store),
        rpl.RoutePolicy(store),
        shutdown.Shutdown(store),
    ]
