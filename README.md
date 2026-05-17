# 🪙 World of Tanks Currency Converter & Live Calculator (v0.4.1)

[![Python Version](https://shields.io)](https://python.org)
[![UI Library](https://shields.io)](https://github.com)
[![Developer](https://shields.io)](https://github.com)

[Русское описание](#русский) | [English Description](#english)

---

## Русский

Современный и стабильный графический калькулятор валют для **World of Tanks / Мира танков**, работающий в режиме реального времени. Скрипт помогает игрокам мгновенно рассчитывать затраты на донат, перевод свободного опыта, покупку кредитов или дней премиум-аккаунта с полным разделением игровой экономики разных регионов.

### ✨ Основные возможности
* **🔄 Расчет в "Прямом Эфире"**: Результаты обновляются автоматически прямо во время ввода чисел. Никаких лишних кнопок!
* **🎛️ Независимый тумблер регионов (LESTA / WG)**: Экономика ивентов и валюта полностью отвязаны от языка интерфейса.
  * **Режим LESTA**: Расчет доната в рублях (**RUB**) с учетом прогрессивных оптовых скидок магазина. Интегрирован модуль контейнеров *«Зов сокола»* (39 руб./шт.).
  * **Режим WG**: Расчет доната в евро (**EUR**). Встроен «жадный» алгоритм, который автоматически собирает любую партию коробок из наиболее выгодных пакетов EU-премиум магазина.
* **🌐 Свободный выбор языка (RU / EN)**: Переключайте язык интерфейса независимо от того, на каком сервере вы играете.
* **🧹 Умная очистка**: При смене региона или вводе данных в новое поле, калькулятор автоматически стирает старые цифры, исключая путаницу между валютами.
* **⌨️ Кросс-раскладный Ctrl + A**: Полная поддержка горячих клавиш «Выделить всё» для быстрой очистки полей, корректно работающая на русской и английской раскладке.
* **🪟 Запуск без консоли**: Код оптимизирован под формат `.pyw` — черное окно терминала Windows больше не появляется при запуске.

### 🚀 Инструкция по запуску
1. Установите графическую библиотеку через командную строку (cmd):
   ```bash
   pip install customtkinter
   ```
2. Запустите файл `WotVconverter.pyw` двойным щелчком мыши.

---

## English

A modern and highly stable real-time graphical currency converter and calculator for **World of Tanks**. This script helps players instantly calculate donation costs, Free XP conversion values, Credits (Silver) purchases, and Premium Account days while keeping regional economics fully separated.

### ✨ Key Features
* **🔄 Real-Time "Live" Calculation**: Results are updated instantly as you type. No unnecessary buttons!
* **🎛️ Independent Region Toggle (LESTA / WG)**: In-game store economics and event lootboxes are completely separated from the UI language.
  * **LESTA Mode**: Calculates costs in Rubles (**RUB**) featuring progressive bulk package discounts. Includes a real-time module for *«Call of the Falcon»* containers (39 RUB/each).
  * **WG Mode**: Calculates costs in Euro (**EUR**). Features a smart greedy algorithm that breaks down any custom number of boxes into the most cost-effective bulk bundles in the EU shop.
* **🌐 Flexible Language Settings (RU / EN)**: Toggle the interface language freely, regardless of your active game server region.
* **🧹 Smart Switch Clearing**: Toggling the region or starting to type in a different field automatically clears all other values to eliminate cross-currency confusion.
* **⌨️ Universal Ctrl + A Support**: Seamless "Select All" shortcut functionality for fast text manipulation, working flawlessly across all keyboard layouts (RU/EN).
* **🪟 Console-less Execution**: Fully optimized for `.pyw` extension deployment, meaning the annoying black terminal window stays completely hidden.

### 🚀 How to Run
1. Install the required GUI library via your terminal:
   ```bash
   pip install customtkinter
   ```
2. Run the `WotVconverter.pyw` file with a simple double-click.

---

## 🛠️ Tech Stack / Стек технологий
* **Language**: Python 3.10+
* **GUI Framework**: CustomTkinter
* **OS-Level Fixes**: `ctypes` library (for crisp fonts and high-DPI scaling on Windows).

## 📝 License
This project is licensed under the [MIT License](LICENSE).

_Disclaimer: This is a fan-made tool and is not affiliated with Wargaming or Lesta Games._
