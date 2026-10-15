# CUPS Driver for Deli P3100DN / P3100DW Laser Printers

English | [Русский](README_ru.md)

Open-source CUPS driver for Deli P3100DN / P3100DW / M3100 series monochrome laser printers on Linux, featuring support for the PCL-XL / Deli Enhanced XL=1.2 protocol, JBIG1 raster compression, and hardware duplex printing (Deli-JPEG).

## Repository Contents

* **`rastertodeli`** — CUPS raster filter converting raster streams into Deli PCL-XL print data using dual-engine architecture:
  * **Engine A:** 1-bit full-page JBIG1 compression for Simplex printing (`ColorDepth=0`, `\xC0\x00\xF8\x34`).
  * **Engine B:** 8-bit 256-line Deli-JPEG band compression for hardware Duplex printing (`ColorDepth=2`, `\xC0\x01\xF8\x35`).
* **`deli-p3100dn.ppd`** — PostScript Printer Description file for CUPS (v1.0).
* **`install.sh`** — Automated installation script for any Linux distribution.
* **`build_deb.py`** — Script to build a Debian/Ubuntu `.deb` package.
* **`LICENSE`** — MIT License.

---

## Installation

### Method 1. Install via Debian Package (`.deb`) — Recommended for Debian / Ubuntu / Astra Linux

Download the pre-built `deli-p3100dn_1.0-1_all.deb` from [Releases](https://github.com/Hamich116/deli-p3100dn-linux-driver/releases) (or build it locally with `python3 build_deb.py`), then install:

```bash
sudo apt install ./deli-p3100dn_1.0-1_all.deb
```

---

### Method 2. Direct Installation via `install.sh` (Other Linux distributions / manual)

1. Clone or download this repository:
   ```bash
   git clone https://github.com/Hamich116/deli-p3100dn-linux-driver.git
   cd deli-p3100dn-linux-driver
   ```
2. Install runtime dependencies:
   ```bash
   # Debian / Ubuntu / Astra Linux:
   sudo apt install python3 libjbig0 jbigkit-bin libjpeg62-turbo python3-pil cups cups-client
   ```
3. Run the installer:
   ```bash
   chmod +x install.sh
   sudo ./install.sh
   ```

*(To uninstall: `sudo ./install.sh --uninstall`)*

---

## Features & Supported Options

* **Paper Formats:** A4, Letter, Legal, Executive, A5, B5, A6.
* **Automatic Duplex (2-Sided Printing):**
  > **Note:** Hardware duplex printing is supported **only for A4** paper.
  * Long-Edge (Standard portrait binding)
  * Short-Edge (Flip / landscape binding)
  * Seamless fallback to simplex for single-page print jobs
  * Automatic blank trailing page generation for odd page counts
* **Print Resolutions:** 600 DPI and 300 DPI.
* **Toner Save (Economode):** On / Off.
* **Input Paper Trays:** Auto Select, Tray 1 (Cassette), Manual Feed Slot.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Disclaimer

This is an unofficial open-source driver developed independently for interoperability with Linux/CUPS. This project is not affiliated with, endorsed by, or sponsored by Deli Group Co., Ltd. All product and company names are trademarks of their respective holders and are used solely for identification purposes.
