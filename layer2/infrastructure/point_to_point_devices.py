from abc import ABC, abstractmethod
from typing import Optional

from layer2.hdlc_base import HdlcLikeBaseFrame
from layer2.infrastructure.network_error import NetworkError
from layer2.infrastructure.network_interface import DeviceWithInterfaces


class PointToPointRouterBase(DeviceWithInterfaces, ABC):
    @abstractmethod
    def __init__(self, num_interfaces, name: Optional[str] = None):
        super().__init__(num_interfaces, name, name_prefix="P2P_ROUTER")

    def receive(self, incoming_interface_num: int, **kwargs) -> None:
        frame: HdlcLikeBaseFrame = kwargs['frame']
        outgoing_interface_num: int = kwargs['outgoing_interface_num']  # In layer 3 we will implement a way to
        # determine the outgoing interface based on the content of the frame (namely, with an ip address routing table)
        self.forward(frame, incoming_interface_num, outgoing_interface_num)

    def forward(self, frame: HdlcLikeBaseFrame, incoming_interface_num,  outgoing_interface_num: int):
        if incoming_interface_num == outgoing_interface_num:
            raise NetworkError("incoming_interface_num is equal to outgoing_interface_num, dropping frame.")
        else:
            if self.get_interface(outgoing_interface_num).connector is None:
                self.say(f"No interface connected on {outgoing_interface_num}, we'll just silently drop the frame.")
            else:
                self.say(f"Forwarding data to interface {outgoing_interface_num}.")
                self.get_interface(outgoing_interface_num).connector.send(frame=frame)

