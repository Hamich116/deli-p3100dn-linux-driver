#!/bin/bash
set -e

# CUPS driver installer for Deli P3100DN / P3100DW laser printers

if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run as root (e.g. sudo ./install.sh)" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILTER_DIR="/usr/lib/cups/filter"
MODEL_DIR="/usr/share/cups/model/deli"
PPD_CUSTOM_DIR="/usr/share/ppd/custom"

case "$1" in
    --uninstall|-u)
        echo "Uninstalling Deli P3100DN CUPS driver..."
        rm -f "${FILTER_DIR}/rastertodeli"
        rm -f "${MODEL_DIR}/deli-p3100dn.ppd"
        rm -f "${PPD_CUSTOM_DIR}/deli-p3100dn.ppd"
        rmdir "${MODEL_DIR}" 2>/dev/null || true

        if which systemctl >/dev/null 2>&1; then
            systemctl restart cups || true
        elif which service >/dev/null 2>&1; then
            service cups restart || true
        fi
        echo "Deli P3100DN driver uninstalled successfully."
        exit 0
        ;;
esac

echo "Installing Deli P3100DN CUPS driver..."

# Check dependencies
MISSING=""
which python3 >/dev/null 2>&1 || MISSING="$MISSING python3"

# Check for jbigkit
if ! ldconfig -p 2>/dev/null | grep -q "libjbig\.so" && ! which pbmtojbg >/dev/null 2>&1; then
    echo "Warning: libjbig / jbigkit-bin not found."
    echo "Recommended: sudo apt install libjbig0 jbigkit-bin"
fi

# Check for libjpeg / PIL
if ! ldconfig -p 2>/dev/null | grep -q "libjpeg\.so" && ! python3 -c "import PIL" >/dev/null 2>&1; then
    echo "Warning: libjpeg / python3-pil not found."
    echo "Recommended: sudo apt install libjpeg62-turbo python3-pil"
fi

if [ -n "$MISSING" ]; then
    echo "Error: Missing required packages:$MISSING" >&2
    exit 1
fi

# Create destination directories
mkdir -p "${FILTER_DIR}"
mkdir -p "${MODEL_DIR}"
mkdir -p "${PPD_CUSTOM_DIR}"

# Install raster filter
cp -f "${SCRIPT_DIR}/rastertodeli" "${FILTER_DIR}/rastertodeli"
chmod 755 "${FILTER_DIR}/rastertodeli"
chown root:root "${FILTER_DIR}/rastertodeli" 2>/dev/null || true

# Install PPD files
cp -f "${SCRIPT_DIR}/deli-p3100dn.ppd" "${MODEL_DIR}/deli-p3100dn.ppd"
chmod 644 "${MODEL_DIR}/deli-p3100dn.ppd"
chown root:root "${MODEL_DIR}/deli-p3100dn.ppd" 2>/dev/null || true

cp -f "${SCRIPT_DIR}/deli-p3100dn.ppd" "${PPD_CUSTOM_DIR}/deli-p3100dn.ppd"
chmod 644 "${PPD_CUSTOM_DIR}/deli-p3100dn.ppd"
chown root:root "${PPD_CUSTOM_DIR}/deli-p3100dn.ppd" 2>/dev/null || true

# Update existing print queues using rastertodeli
if [ -d /etc/cups/ppd ]; then
    for ppd in /etc/cups/ppd/*.ppd; do
        if [ -f "$ppd" ] && grep -q "rastertodeli" "$ppd" 2>/dev/null; then
            cp -f "${MODEL_DIR}/deli-p3100dn.ppd" "$ppd" || true
        fi
    done
fi

# Restart CUPS service
if which systemctl >/dev/null 2>&1; then
    systemctl restart cups || true
elif which service >/dev/null 2>&1; then
    service cups restart || true
fi

# Re-enable and accept jobs on queues using this driver
if which cupsenable >/dev/null 2>&1 && which lpstat >/dev/null 2>&1; then
    for q in $(lpstat -p 2>/dev/null | awk '{print $2}'); do
        if [ -f "/etc/cups/ppd/${q}.ppd" ] && grep -q "rastertodeli" "/etc/cups/ppd/${q}.ppd" 2>/dev/null; then
            cupsenable "$q" 2>/dev/null || true
            cupsaccept "$q" 2>/dev/null || true
        fi
    done
fi

echo "Deli P3100DN driver installed successfully!"
echo "You can now add your printer via GUI Settings, http://localhost:631, or lpadmin."
