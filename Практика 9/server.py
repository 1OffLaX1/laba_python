import argparse
import logging
import socket
from threading import Event, Thread
from domain import ItemRepository, WarehouseService, NotFoundError
from protocol import Connection, ProtocolError, FrameError, validate_request


class WarehouseServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 5007,
                 timeout: float = 60, service: WarehouseService | None = None) -> None:
        self.service = service if service is not None else WarehouseService(ItemRepository())
        self.timeout = timeout
        self.stop = Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((host, port))
            self.socket.listen()
            self.socket.settimeout(0.2)
        except OSError:
            self.socket.close()
            raise
        self.address = self.socket.getsockname()

    def serve_forever(self) -> None:
        logging.info("Сервер запущен: %s:%s", *self.address)
        while not self.stop.is_set():
            try:
                client, address = self.socket.accept()
            except socket.timeout:
                continue
            except OSError:
                if not self.stop.is_set():
                    logging.exception("Ошибка приёма соединения")
                break
            Thread(target=self.handle_client, args=(client, address), daemon=True).start()

    def handle_client(self, client: socket.socket, address: tuple) -> None:
        logging.info("Клиент подключён: %s", address)
        client.settimeout(self.timeout)
        connection = Connection(client)
        try:
            while not self.stop.is_set():
                try:
                    request = connection.receive()
                    if request is None:
                        break
                    command, data = validate_request(request)
                    logging.info("Команда %s от %s", command, address)
                    result = self.service.execute(command, data)
                    response = {"status": "ok", "data": result}
                    logging.info("Команда %s выполнена", command)
                except FrameError as error:
                    logging.warning("Ошибка границ сообщения: %s", error)
                    connection.send({"status": "error", "error": str(error)})
                    break
                except socket.timeout:
                    logging.warning("Тайм-аут клиента: %s", address)
                    connection.send({"status": "error", "error": "Тайм-аут ожидания запроса"})
                    break
                except (ProtocolError, ValueError, TypeError, KeyError, NotFoundError) as error:
                    logging.warning("Ошибка запроса от %s: %s", address, error)
                    response = {"status": "error", "error": str(error)}
                connection.send(response)
        except (OSError, ProtocolError) as error:
            logging.warning("Ошибка соединения %s: %s", address, error)
        finally:
            connection.close()
            client.close()
            logging.info("Клиент отключён: %s", address)

    def close(self) -> None:
        self.stop.set()
        self.socket.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Учебный TCP-сервер склада")
    parser.add_argument("--port", type=int, default=5007)
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535 or not 0 < args.timeout < float("inf"):
        parser.error("Порт: 1–65535; тайм-аут: положительное конечное число")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        server = WarehouseServer(port=args.port, timeout=args.timeout)
    except OSError as error:
        print("Не удалось запустить сервер:", error)
        return
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    finally:
        server.close()


if __name__ == "__main__":
    main()
