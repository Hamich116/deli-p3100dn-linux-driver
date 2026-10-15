# Драйвер CUPS для лазерных принтеров Deli P3100DN / P3100DW

[English](README.md) | Русский

Драйвер с открытым исходным кодом для монохромных лазерных принтеров Deli серии P3100DN / P3100DW / M3100 под Linux (CUPS) с поддержкой протокола PCL-XL / Deli Enhanced XL=1.2, компрессии JBIG1 и аппаратного дуплекса (Deli-JPEG).

## Содержимое репозитория

* **`rastertodeli`** — фильтр-конвертер растра CUPS в поток команд PCL-XL / Deli Enhanced XL=1.2 с двухдвижковой архитектурой:
  * **Engine A:** 1-битный полностраничный JBIG1 для односторонней печати (Simplex, `ColorDepth=0`, `\xC0\x00\xF8\x34`).
  * **Engine B:** 8-битный 256-строчный полосовой Deli-JPEG для аппаратного дуплекса (Duplex, `ColorDepth=2`, `\xC0\x01\xF8\x35`).
* **`deli-p3100dn.ppd`** — файл описания принтера для CUPS (PostScript Printer Description v1.0).
* **`install.sh`** — скрипт автоматической установки драйвера в систему CUPS.
* **`build_deb.py`** — скрипт сборки установочного `.deb` пакета для Debian / Ubuntu / Astra Linux.
* **`LICENSE`** — лицензия MIT.

---

## Установка

### Способ 1. Быстрая установка через `install.sh` (любой дистрибутив Linux)

1. Клонируйте репозиторий или скачайте архив:
   ```bash
   git clone https://github.com/Hamich116/deli-p3100dn-linux-driver.git
   cd deli-p3100dn-linux-driver
   ```
2. Установите необходимые системные зависимости:
   ```bash
   # Debian / Ubuntu / Astra Linux:
   sudo apt install python3 libjbig0 jbigkit-bin libjpeg62-turbo python3-pil cups cups-client
   ```
3. Запустите скрипт установки:
   ```bash
   chmod +x install.sh
   sudo ./install.sh
   ```

*(Для удаления драйвера выполните: `sudo ./install.sh --uninstall`)*

---

### Способ 2. Сборка и установка через .deb пакет (Debian / Ubuntu / Astra Linux)

1. Соберите `.deb` пакет:
   ```bash
   python3 build_deb.py
   ```
2. Установите созданный пакет:
   ```bash
   sudo apt install ./deli-p3100dn_1.0-1_all.deb
   ```

---

## Поддерживаемые функции

* **Форматы бумаги:** A4, Letter, Legal, Executive, A5, B5, A6.
* **Автоматическая двусторонняя печать (Duplex):**
  > **Примечание:** Аппаратный дуплекс поддерживается **только для бумаги формата A4**.
  * Переплет по длинному краю (Long-Edge / книжная ориентация)
  * Переплет по короткому краю (Short-Edge / альбомная ориентация)
  * Автоматический переход в режим Simplex для 1-страничных заданий
  * Автоматическое добавление пустой оборотной страницы при нечетном числе страниц
* **Разрешение печати:** 600 DPI и 300 DPI.
* **Режим экономии тонера (Economode / Toner Save):** Вкл / Выкл.
* **Источники бумаги (лотки):** автовыбор, нижняя кассета, лоток ручной подачи.

---

## Лицензия / License

Проект распространяется под свободной лицензией [MIT](LICENSE).

---

## Disclaimer

This is an unofficial open-source driver developed independently for interoperability with Linux/CUPS. This project is not affiliated with, endorsed by, or sponsored by Deli Group Co., Ltd. All product and company names are trademarks of their respective holders and are used solely for identification purposes.
