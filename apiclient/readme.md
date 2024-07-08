Пример использования:

```python
import apiclient

vdi = apiclient.Client(  # Параметры подключения
    '10.1.1.1',  # адрес брокера
    'admin',  # аутентификатор
    'root',  # пользователь
    'udsmam0'  # пароль
)

try:
    vdi.login()  # Подключение к брокеру
    print(vdi.get_config())  # Вывод на экран конфигурации брокера
    vdi.logout()  # Завершение сессии
except ValueError as e:
    print('Invalid data: {}'.format(e))
except Exception as e:
    raise('Caught exception: {}'.format(e))
```
