from ipaddress import IPv4Address, IPv6Address

from bitstring import BitArray

from layer3.ip.ipv4 import IPv4Packet, IPv4Flag, IPv4Options, IPv4Header
from layer3.ip.ipv6 import IPv6Packet, IPv6Header
from layer3.ip.shared import ECN, DSCP, IPProtocol


def packet_decoder(data: bytes):
    version = get_ip_version(data)
    if version == IPv4Packet.VERSION:
        return ipv4_from_bytes(data)
    elif version == IPv6Packet.VERSION:
        return ipv6_from_bytes(data)
    else:
        raise ValueError(f"Unsupported IP version: {version}")


def get_ip_version(raw_data: bytes) -> int:
    return BitArray(auto=raw_data[:1])[:4].uint


def ipv4_from_bytes(data: bytes):
    fixed_header = BitArray(auto=data[:20])

    version: int = fixed_header[:4].uint
    if version != IPv4Packet.VERSION:
        raise ValueError("Version of IPv4 should be 4.")

    ihl: int = fixed_header[4:8].uint
    dscp = DSCP.from_int(fixed_header[8:14].uint)
    ecn = ECN(fixed_header[14:16].uint)

    total_len: int = fixed_header[16:32].uint
    if total_len < 20:
        raise ValueError(f"total_length of the packet is invalid, expected > 20 but got {total_len}")

    identification: int = fixed_header[32:48].uint
    flags = IPv4Flag.from_bits(fixed_header[48:52])
    fragment_offset: int = fixed_header[52:64].uint
    ttl: int = fixed_header[64:72].uint
    protocol = IPProtocol.from_int(fixed_header[72:80].uint)
    header_checksum = fixed_header[80:96]
    source = IPv4Address(fixed_header[96:128].uint)
    destination = IPv4Address(fixed_header[128:160].uint)

    options_bytes = [data[4 * i: 4 * (i + 1)] for i in range(5, ihl)]
    options = [IPv4Options.from_int(int.from_bytes(option_bytes, byteorder='big')) for option_bytes in
               options_bytes]

    payload = data[4 * ihl:total_len]

    header = IPv4Header(dscp, ecn, identification, flags, fragment_offset, ttl, protocol, len(payload), source,
                        destination, *options).overwrite_checksum(header_checksum)
    if not header.verify_checksum():
        raise ValueError("Checksum of this IPv4 header invalid")

    return IPv4Packet(header, payload)


def ipv6_from_bytes(data: bytes):
    fixed_header = BitArray(auto=data[:40])

    version: int = fixed_header[:4].uint
    if version != IPv6Packet.VERSION:
        raise ValueError("Version of IPv6 should be 6.")

    dscp = DSCP.from_int(fixed_header[4:10].uint)
    ecn = ECN(fixed_header[10:12].uint)
    flow_label: int = fixed_header[12:32].uint
    payload_len: int = fixed_header[32:48].uint
    next_header = IPProtocol.from_int(fixed_header[48:56].uint)
    hop_limit: int = fixed_header[56:64].uint
    source = IPv6Address(fixed_header[64:192].uint)
    destination = IPv6Address(fixed_header[192:320].uint)

    payload = data[40:40 + payload_len]
    header = IPv6Header(dscp, ecn, flow_label, payload_len, next_header, hop_limit, source, destination)

    return IPv6Packet(header, payload)
