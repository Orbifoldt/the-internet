import uuid
from collections import deque
from queue import Queue, Empty
from threading import Timer
from typing import Iterable, Optional, TypeVar

import rx
from bitstring import BitArray
from rx import create, Observable
import rx.operators as ops

T = TypeVar("T")

# def push_five_strings(observer, scheduler):
#     observer.on_next("Alpha")
#     observer.on_next("Beta")
#     observer.on_next("Gamma")
#     observer.on_next("Delta")
#     observer.on_next("Epsilon")
#     observer.on_completed()
#
#
# source = create(push_five_strings)
#
# source.subscribe(
#     on_next=lambda i: print("Received {0}".format(i)),
#     on_error=lambda e: print("Error Occurred: {0}".format(e)),
#     on_completed=lambda: print("Done!"),
# )


# obs = rx.interval(1)
# obs.subscribe(on_next=print)
from rx.subject import Subject


class Transmitter(object):
    def __init__(self) -> None:
        self.id = uuid.uuid4()
        self.backlog = Queue()
        self.iterable_source = self.itr_src()
        self.observable = rx.interval(0.1).pipe(
            ops.map(lambda _: next(self.iterable_source))
        )

    def itr_src(self):
        while True:
            try:
                nxt = self.backlog.get_nowait()
                yield nxt
            except Empty:
                yield None

    def _put_into_queue(self, elts: Iterable):
        for elt in elts:
            self.backlog.put(elt)

    def send(self, data: BitArray):
        self._put_into_queue(data)


class Connection(object):
    def __init__(self):
        self.id = uuid.uuid4()
        self.observable = rx.empty()
        self.connectors: list[Transmitter] = []

    def connect(self, transmitter: Transmitter, on_error=None, on_completed=None, on_next=None):
        self.connectors.append(transmitter)
        self._update_observable()
        self.observable.subscribe(on_error, on_completed, on_next)

    def _update_observable(self):
        self.observable = rx.zip(*[x.observable for x in self.connectors]).pipe(ops.map(self.merge))

    def disconnect(self, transmitter: Transmitter):
        self.connectors = list(filter(lambda x: x.id != transmitter.id, self.connectors))
        self._update_observable()

    # def active(self, ss: Observable[Observable[T]]):
    #     activeStreams = Subject()
    #     elements = []
    #     subscriptions = []
    #
    #     def lmbda(s: Observable):
    #         include = True
    #         def lmbda2():
    #             include = False
    #         subscription = s.subscribe(on_next=lmbda2)
    #
    #     ss.subscribe(observer= )

    @staticmethod
    def merge(bools):
        x = 0
        for b in bools:
            if b is None:
                pass
            elif b:
                x += 1
            else:
                x -= 1
        return None if x == 0 else (x > 0)


class Server(object):
    def __init__(self, id=None):
        self.id = uuid.uuid4() if id is None else id
        self.transmitter = Transmitter()
        self.received = Queue()
        self.say("Initialized")

    def connect_to(self, conn: Connection):
        conn.connect(
            self.transmitter,
            on_next=lambda b: self.say(f"Received '{b}'"),
            # on_next=self.received.put,
            on_error=lambda ex: self.say(f"Connection {conn.id} threw error: {ex}"),
            on_completed=lambda: self.disconnect(conn)
        )

    def disconnect(self, conn: Connection):
        conn.disconnect(self.transmitter)
        self.say(f"Connection {conn.id} was closed.")

    def send(self, bits: BitArray):
        self.transmitter.send(bits)

    def say(self, text):
        print(f"[server-{self.id}]: {text}")


# class Receiver(object):
#     def __init__(self, observable: Observable):
#         self.observer = observable.subscribe(
#             on_next=lambda x: print("Received: " + ("None" if x is None else x.__str__())),
#             on_error=print,
#             on_completed=print("Completed"))


# sender = Sender()
# sender._put_into_queue([i.to_bytes(1, byteorder='big') for i in range(32, 127)])
#
# t1 = Timer(10, lambda: [print("hello"), sender._put_into_queue(["XXX" for x in range(10)])])
# t2 = Timer(10, lambda: sender._put_into_queue(["YYY" for x in range(10)]))
# t3 = Timer(10, lambda: sender._put_into_queue(["ZZZ" for x in range(10)]))
# t1.start()
# t2.start()
# t3.start()

# receiver = Receiver(sender.observable)

Timer(20, lambda: print("OKKOKKOK")).start()

a = Server("A")
b = Server("B")
conn = Connection()
a.connect_to(conn)
b.connect_to(conn)

a.send(BitArray(bin="101"))

while not b.received.empty():
    print(b.received.get())
