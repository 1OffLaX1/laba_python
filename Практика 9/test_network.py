import logging
import socket
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Thread
from domain import Item, ItemRepository, WarehouseService, NotFoundError
from protocol import (Connection, ProtocolError, FrameError, encode_message,
                      decode_message, validate_request)
from server import WarehouseServer


class RepositoryTests(unittest.TestCase):
    def test_add_get(self):
        repository = ItemRepository()
        item = Item(1, "Болт", 10, 5)
        repository.add(item)
        self.assertEqual(repository.get_all(), [item])
        self.assertEqual(repository.get(1).name, "Болт")
        with self.assertRaises(ValueError):
            repository.add(item)

    def test_update_delete(self):
        repository = ItemRepository()
        repository.add(Item(1, "Болт", 10, 5))
        repository.update(Item(1, "Болт", 20, 5))
        self.assertEqual(repository.get(1).quantity, 20)
        repository.delete(1)
        with self.assertRaises(NotFoundError):
            repository.get(1)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = WarehouseService(ItemRepository())

    def test_create_and_get(self):
        item = self.service.execute("create", dict(name="Болт", quantity=3, minimum=5))
        self.assertEqual(item["id"], 1)
        self.assertEqual(self.service.execute("get", {"id": 1})["name"], "Болт")

    def test_stock_boundaries(self):
        for count in [0, 4, 5, 6]:
            self.service.execute("create", dict(name="Болт", quantity=count, minimum=5))
        stocks = self.service.execute("check_stock", {})
        self.assertEqual([x["shortage"] for x in stocks], [5, 1, 0, 0])
        self.assertEqual([x["enough"] for x in stocks], [False, False, True, True])

    def test_update_is_atomic(self):
        self.service.execute("create", dict(name="Болт", quantity=3, minimum=5))
        with self.assertRaises(ValueError):
            self.service.execute("update", {"id": 1, "quantity": -1})
        self.assertEqual(self.service.execute("get", {"id": 1})["quantity"], 3)
        self.service.execute("update", {"id": 1, "quantity": 8})
        self.assertEqual(self.service.execute("check_stock", {"id": 1})[0]["shortage"], 0)

    def test_delete(self):
        self.service.execute("create", dict(name="Болт", quantity=3, minimum=5))
        self.service.execute("delete", {"id": 1})
        self.assertEqual(self.service.execute("list", {}), [])

    def test_invalid(self):
        for count in [-1, 1.5, True, "5"]:
            with self.assertRaises(ValueError):
                self.service.execute("create", dict(name="Болт", quantity=count, minimum=5))
        with self.assertRaises(ValueError):
            self.service.execute("unknown", {})
        with self.assertRaises(NotFoundError):
            self.service.execute("get", {"id": 99})
        with self.assertRaises(TypeError):
            self.service.execute("create", {})


class ProtocolTests(unittest.TestCase):
    def test_round_trip(self):
        message = {"command": "create", "data": {"name": "Болт\nМ8"}}
        self.assertEqual(decode_message(encode_message(message)), message)
        self.assertEqual(encode_message(message).count(b"\n"), 1)

    def test_invalid_json(self):
        for data in [b"{", b"[]", b"\xff", b'{"value":NaN}']:
            with self.assertRaises(ProtocolError):
                decode_message(data)

    def test_required_fields(self):
        for request in [{}, {"command": "list"}, {"command": 1, "data": {}},
                        {"command": "list", "data": []}]:
            with self.assertRaises(ProtocolError):
                validate_request(request)

    def test_client_timeout(self):
        left, right = socket.socketpair()
        connection = Connection(left)
        left.settimeout(0.05)
        try:
            with self.assertRaises(socket.timeout):
                connection.receive()  # Вторая сторона не отправляет ответ.
        finally:
            connection.close()
            left.close()
            right.close()

    def test_incomplete_frame(self):
        left, right = socket.socketpair()
        connection = Connection(left)
        right.sendall(b'{"command":"list"}')
        right.shutdown(socket.SHUT_WR)
        try:
            with self.assertRaises(FrameError):
                connection.receive()
        finally:
            connection.close()
            left.close()
            right.close()


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.old_log_level = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        self.server = WarehouseServer(port=0, timeout=1)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.close()
        self.thread.join(2)
        logging.disable(self.old_log_level)
        self.assertFalse(self.thread.is_alive())

    def connect(self):
        sock = socket.create_connection(self.server.address, timeout=2)
        connection = Connection(sock)
        self.addCleanup(sock.close)
        self.addCleanup(connection.close)
        return sock, connection

    def test_all_commands_over_tcp(self):
        _, connection = self.connect()
        queries = [("create", dict(name="Болт", quantity=3, minimum=5)),
                   ("list", {}), ("get", {"id": 1}),
                   ("update", {"id": 1, "quantity": 4}),
                   ("check_stock", {"id": 1}), ("delete", {"id": 1})]
        results = []
        for command, data in queries:
            connection.send({"command": command, "data": data})
            response = connection.receive()
            self.assertEqual(response["status"], "ok")
            results.append(response["data"])
        self.assertEqual(results[4][0]["shortage"], 1)

    def test_invalid_request_then_recovery(self):
        sock, connection = self.connect()
        for payload in [b"{\n", b"[]\n", b'{}\n',
                        encode_message({"command": "unknown", "data": {}}),
                        encode_message({"command": "create", "data": {}})]:
            sock.sendall(payload)
            self.assertEqual(connection.receive()["status"], "error")
        connection.send({"command": "list", "data": {}})
        self.assertEqual(connection.receive(), {"status": "ok", "data": []})

    def test_split_and_joined_messages(self):
        sock, connection = self.connect()
        request = encode_message({"command": "create", "data":
                                  dict(name="Болт", quantity=1, minimum=5)})
        split = request.index("Б".encode("utf-8")) + 1
        sock.sendall(request[:split])
        time.sleep(0.01)
        sock.sendall(request[split:])
        self.assertEqual(connection.receive()["status"], "ok")
        query = encode_message({"command": "list", "data": {}})
        sock.sendall(query + query)
        self.assertEqual(connection.receive()["status"], "ok")
        self.assertEqual(connection.receive()["status"], "ok")

    def test_long_message(self):
        _, connection = self.connect()
        name = "Б" * 3000
        connection.send({"command": "create", "data": dict(name=name, quantity=1, minimum=0)})
        self.assertEqual(connection.receive()["data"]["name"], name)

    def test_three_simultaneous_clients(self):
        barrier = Barrier(3)
        def client(number):
            with socket.create_connection(self.server.address, timeout=2) as sock:
                connection = Connection(sock)
                try:
                    barrier.wait(timeout=2)
                    connection.send({"command": "create", "data":
                                     dict(name=f"Товар {number}", quantity=number, minimum=5)})
                    result = connection.receive()
                    barrier.wait(timeout=2)
                    connection.send({"command": "list", "data": {}})
                    self.assertEqual(len(connection.receive()["data"]), 3)
                    return result["data"]["id"]
                finally:
                    connection.close()
        with ThreadPoolExecutor(max_workers=3) as pool:
            ids = list(pool.map(client, [1, 2, 3]))
        self.assertEqual(sorted(ids), [1, 2, 3])

    def test_server_timeout(self):
        self.server.timeout = 0.05
        _, connection = self.connect()
        response = connection.receive()
        self.assertEqual(response["status"], "error")
        self.assertIn("Тайм-аут", response["error"])
