# py3xui

**py3xui** — это Python API-клиент для работы с веб-панелью **3X-UI**.  
Он позволяет управлять инбаундами, клиентами и их трафиком напрямую через Python-код.

---


```python
from py3xui import Client

# создаём клиента (без SSL-сертификата)
client = Client(
    host="127.0.0.1",
    port="54321",
    web_base_path="vless",
    ssl_certificate=False
)

# получаем список всех инбаундов
inbounds = client.inbounds()
print(inbounds)

# добавляем новый инбаунд
new_inbound = client.add_inbound(
    name_inbound="TestInbound",
    port=1080,
    email="user@example.com",
    total_gb=5,  # в гигабайтах
    expiry_time=30  # в днях
)
print(new_inbound)

# добавляем клиента к инбаунду
client.add_client_to_inbound(
    inbound_id=None,  # если None, возьмётся последний инбаунд
    email="client1@example.com",
    total_gb=10,
    expiry_time=60,
    enable=True
)

# обновляем клиента
client.update_client(
    email="client1@example.com",
    total_gb=20,
    enable=False
)

# сброс трафика конкретного клиента
client.reset_client_traffic("client1@example.com")

# удаление клиента
client.delete_client("client1@example.com")

```

##  🔑 Основные возможности

- Авторизация и сохранение cookies в базе

- Управление инбаундами:

    - inbounds() — список инбаундов

    - inbound(inbound_id) — получить инбаунд по ID

    - add_inbound(...) — добавить новый инбаунд

    - delete_inbound(inbound_id) — удалить инбаунд

- Управление клиентами:

    - add_client_to_inbound(...) — добавить клиента в инбаунд

    - update_client(...) — обновить параметры клиента

    - delete_client(email) — удалить клиента

    - get_traffics_with_email(email) — получить статистику трафика клиента

    - reset_client_traffic(email) — сбросить трафик клиента

- Общие операции:

    - reset_all_traffics() — сбросить трафик у всех клиентов

    - get_online_clients() — получить список онлайн-клиентов
