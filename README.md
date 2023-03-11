# torrserv_tgbot

Сканер серверов Torrserver без пароля

## Установка

+ pip install asyncio
+ pip install lxml
+ pip install masscan (Linux) или https://github.com/Arryboom/MasscanForWindows
+ pip install matplotlib

## bot.py

Позволяет выбрать файл с ip-адресами подсетей из папки 'subnets' и начать поиск серверов.
Все найденные адреса записывает в 'result.txt'. Является управляющей программой

## config.txt

Для указания портов, пример:

> ports = 8090,8091,1000-1100

## check.py

Вы также можете запустить отдельно данную подпрограмму для поиска серверов из большого файла после masscan.
Читает адреса из 'ip.txt'. Сохраняет результат в 'final.txt'
Пример запуска:
+ получаем ip.txt
> masscan -p8090 подсеть -oL ip.txt --rate=5000 --wait=0
+ сканируем
> python3 checkip.py
