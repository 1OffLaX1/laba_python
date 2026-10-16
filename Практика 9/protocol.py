import json
import socket

MAX_MESSAGE = 1024 * 1024  # Не более 1 МиБ на один JSON-документ.


class ProtocolError(Exception):
    pass


class FrameError(ProtocolError):
    """Нарушена граница сообщения; соединение нужно закрыть."""


def encode_message(message: dict) -> bytes:
    if not isinstance(message, dict):
        raise ProtocolError("Сообщение должно быть JSON-объектом")
    try:
        data = (json.dumps(message, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ProtocolError("Не удалось закодировать сообщение") from error
    if len(data) > MAX_MESSAGE:
        raise FrameError("Сообщение слишком большое")
    return data


def reject_constant(value: str) -> None:
    raise ValueError(f"Недопустимое значение JSON: {value}")


def decode_message(data: bytes) -> dict:
    try:
        message = json.loads(data.decode("utf-8"), parse_constant=reject_constant)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ProtocolError("Некорректный JSON или UTF-8") from error
    if not isinstance(message, dict):
        raise ProtocolError("Ожидается JSON-объект")
    return message


def validate_request(request: dict) -> tuple[str, dict]:
    if not isinstance(request.get("command"), str) or not isinstance(request.get("data"), dict):
        raise ProtocolError("Обязательные поля: command (строка), data (объект)")
    return request["command"], request["data"]


class Connection:
    def __init__(self, sock: socket.socket) -> None:
        self.socket = sock
        self.reader = sock.makefile("rb")

    def send(self, message: dict) -> None:
        self.socket.sendall(encode_message(message))

    def receive(self) -> dict | None:
        # readline сохраняет неполные и объединённые TCP-пакеты в буфере.
        line = self.reader.readline(MAX_MESSAGE + 1)
        if not line:
            return None
        if len(line) > MAX_MESSAGE or not line.endswith(b"\n"):
            raise FrameError("Слишком длинное или незавершённое сообщение")
        return decode_message(line)

    def close(self) -> None:
        self.reader.close()
