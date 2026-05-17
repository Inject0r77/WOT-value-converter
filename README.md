# WOT-value-converter
Real-time currency converter to WOT (WG/LESTA) with many variables.
# 🪙 World of Tanks Currency Converter & Live Calculator

[![Python Version](https://shields.io)](https://python.org)
[![UI Library](https://shields.io)](https://github.com)
[![Game](https://shields.io)](https://worldoftanks.ru)

[Русское описание](#русский) | [English Description](#english)

---

## Русский

Современный графический калькулятор валют для **World of Tanks (WoT)**, работающий в режиме реального времени. Скрипт помогает игрокам мгновенно рассчитывать затраты на донат, перевод свободного опыта, покупку кредитов или дней премиум-аккаунта с учетом региональной экономики и оптовых скидок.

### ✨ Основные возможности
* **🔄 Расчет в "Прямом Эфире"**: Результаты обновляются автоматически прямо во время ввода чисел.
* **🌐 Мультиязычность (RU/EN)**: Мгновенное переключение интерфейса и автоматическая адаптация под валюту региона (**RUB** или **EUR**).
* **📉 Динамическая сетка цен**:
  * В режиме **RU** скрипт учитывает прогрессивную скидку игрового магазина при покупке золота большими пакетами.
  * В режиме **EN** производится ювелирный расчет стоимости в **Евро (€)** на основе официальной сетки пакетов EU-региона.
* **⭐ Обратная конвертация**: Введите желаемое количество свободного опыта, и калькулятор сам посчитает, сколько золота и денег для этого потребуется.
* **🎛️ Интерактивные тумблеры акций**:
  * Включение праздничного курса перевода опыта (**1 к 35** вместо базового 1 к 25).
  * Включение внутриигровой скидки **15%** на покупку премиум-аккаунта.
* **⌨️ Удобство использования**: Полная поддержка горячих клавиш `Ctrl + A` (Выделить всё) для быстрой очистки полей в любой раскладке клавиатуры.

### 🚀 Инструкция по запуску
1. Установите графическую зависимость через командную строку (cmd):
   ```bash
   pip install customtkinter
   ```
2. Переименуйте файл скрипта в `wot_live_calc.pyw` (чтобы скрыть черное окно консоли) и запустите его двойным щелчком мыши.

---

## English

A modern, real-time graphical currency converter and calculator for **World of Tanks (WoT)**. This script helps players instantly calculate donation costs, Free XP conversion values, Credits (Silver) purchases, and Premium Account days based on regional game economics and package discounts.

### ✨ Key Features
* **🔄 Real-Time "Live" Calculation**: Results are updated automatically as you type. No unnecessary buttons!
* **🌐 Multi-language Support (RU/EN)**: Instant UI translation and automatic currency adaptation (**RUB** or **EUR**) depending on the selected region.
* **📉 Dynamic Price Grid**:
  * In **RU mode**, the script accounts for progressive bulk discounts when buying large amounts of Gold.
  * In **EN mode**, it accurately calculates the cost in **Euro (€)** based on the official EU shop package grid.
* **⭐ Reverse Conversion**: Enter the desired amount of Free XP, and the calculator will find exactly how much Gold and money you need.
* **🎛️ Interactive Special Offer Toggles**:
  * Activate festive Free XP conversion events (**1 to 35** instead of the base 1 to 25 rate).
  * Apply an in-game **15% discount** on Premium Account purchases.
* **⌨️ Great UX**: Seamless `Ctrl + A` (Select All) shortcut support for quick field clearing, fully working across different keyboard layouts.

### 🚀 How to Run
1. Install the required GUI library via your terminal:
   ```bash
   pip install customtkinter
   ```
2. Rename the script file to `wot_live_calc.pyw` (to completely hide the black console window) and run it with a simple double-click.

---

## 🛠️ Tech Stack / Стек технологий
* **Language**: Python 3.10+
* **GUI Framework**: CustomTkinter
* **OS-Level Fixes**: `ctypes` library (for crisp fonts and high-DPI scaling on Windows).

## 📝 License
This project is licensed under the [MIT License](LICENSE).

_Disclaimer: This is a fan-made tool and is not affiliated with Wargaming or Lesta Games._
