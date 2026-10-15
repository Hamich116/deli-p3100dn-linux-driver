#!/usr/bin/env python3
"""
Builds the Debian package (.deb) for the Deli P3100DN CUPS driver.
"""

import os
import io
import tarfile
import time

base_dir = os.path.dirname(os.path.abspath(__file__))
raster_path = os.path.join(base_dir, 'rastertodeli')
ppd_path = os.path.join(base_dir, 'deli-p3100dn.ppd')
deb_path = os.path.join(base_dir, 'deli-p3100dn_1.0-1_all.deb')

# Ensure Unix line endings
with open(raster_path, 'rb') as f:
    raster_content = f.read().replace(b'\r\n', b'\n')
with open(raster_path, 'wb') as f:
    f.write(raster_content)

with open(ppd_path, 'rb') as f:
    ppd_content = f.read().replace(b'\r\n', b'\n')
with open(ppd_path, 'wb') as f:
    f.write(ppd_content)

# 1. debian-binary
debian_binary = b"2.0\n"

# 2. control.tar.gz
control_content = (
    "Package: deli-p3100dn\n"
    "Version: 1.0-1\n"
    "Section: text\n"
    "Priority: optional\n"
    "Architecture: all\n"
    "Depends: python3, libjbig0 | jbigkit-bin, jbigkit-bin, libjpeg62-turbo | libjpeg8 | python3-pil, cups, cups-client, cups-filters\n"
    "Maintainer: Open Source CUPS Driver Team <driver@localhost>\n"
    "Description: CUPS driver for Deli P3100DN / M3100 series laser printers\n"
    " This package provides the rastertodeli CUPS raster filter and PPD file\n"
    " for Deli P3100DN / P3100DW / M3100 series monochrome laser printers\n"
    " with automatic duplex support (Engine A JBIG1 + Engine B Deli-JPEG).\n"
).encode('utf-8')

postinst_content = (
    "#!/bin/sh\n"
    "set -e\n"
    "chmod 755 /usr/lib/cups/filter/rastertodeli || true\n"
    "if [ -d /etc/cups/ppd ]; then\n"
    "    for ppd_file in /etc/cups/ppd/*.ppd; do\n"
    "        if [ -f \"$ppd_file\" ] && grep -q \"rastertodeli\" \"$ppd_file\" 2>/dev/null; then\n"
    "            cp -f /usr/share/cups/model/deli/deli-p3100dn.ppd \"$ppd_file\" || true\n"
    "        fi\n"
    "    done\n"
    "fi\n"
    "if which systemctl >/dev/null 2>&1; then\n"
    "    systemctl restart cups || true\n"
    "elif which service >/dev/null 2>&1; then\n"
    "    service cups restart || true\n"
    "fi\n"
    "if which cupsenable >/dev/null 2>&1 && which lpstat >/dev/null 2>&1; then\n"
    "    for q in $(lpstat -p 2>/dev/null | awk '{print $2}'); do\n"
    "        if [ -f \"/etc/cups/ppd/${q}.ppd\" ] && grep -q \"rastertodeli\" \"/etc/cups/ppd/${q}.ppd\" 2>/dev/null; then\n"
    "            cupsenable \"$q\" 2>/dev/null || true\n"
    "            cupsaccept \"$q\" 2>/dev/null || true\n"
    "        fi\n"
    "    done\n"
    "fi\n"
    "exit 0\n"
).encode('utf-8')

postrm_content = (
    "#!/bin/sh\n"
    "set -e\n"
    "if which systemctl >/dev/null 2>&1; then\n"
    "    systemctl restart cups || true\n"
    "fi\n"
    "exit 0\n"
).encode('utf-8')

now = int(time.time())

control_buf = io.BytesIO()
with tarfile.open(fileobj=control_buf, mode='w:gz') as tar:
    def add_mem_file(name, content, mode):
        ti = tarfile.TarInfo(name=name)
        ti.size = len(content)
        ti.mtime = now
        ti.mode = mode
        ti.uname = 'root'
        ti.gname = 'root'
        tar.addfile(ti, io.BytesIO(content))

    add_mem_file('./control', control_content, 0o644)
    add_mem_file('./postinst', postinst_content, 0o755)
    add_mem_file('./postrm', postrm_content, 0o755)

control_tar_gz = control_buf.getvalue()

# 3. data.tar.gz
data_buf = io.BytesIO()
with tarfile.open(fileobj=data_buf, mode='w:gz') as tar:
    def add_dir(name):
        ti = tarfile.TarInfo(name=name)
        ti.type = tarfile.DIRTYPE
        ti.mode = 0o755
        ti.mtime = now
        ti.uname = 'root'
        ti.gname = 'root'
        tar.addfile(ti)

    for d in [
        './usr',
        './usr/lib',
        './usr/lib/cups',
        './usr/lib/cups/filter',
        './usr/share',
        './usr/share/cups',
        './usr/share/cups/model',
        './usr/share/cups/model/deli',
        './usr/share/ppd',
        './usr/share/ppd/custom',
    ]:
        add_dir(d)

    # Filter executable
    ti = tarfile.TarInfo(name='./usr/lib/cups/filter/rastertodeli')
    ti.size = len(raster_content)
    ti.mtime = now
    ti.mode = 0o755
    ti.uname = 'root'
    ti.gname = 'root'
    tar.addfile(ti, io.BytesIO(raster_content))

    # PPD in cups model
    ti = tarfile.TarInfo(name='./usr/share/cups/model/deli/deli-p3100dn.ppd')
    ti.size = len(ppd_content)
    ti.mtime = now
    ti.mode = 0o644
    ti.uname = 'root'
    ti.gname = 'root'
    tar.addfile(ti, io.BytesIO(ppd_content))

    # PPD also in /usr/share/ppd/custom for printer-config GUI auto-discovery
    ti = tarfile.TarInfo(name='./usr/share/ppd/custom/deli-p3100dn.ppd')
    ti.size = len(ppd_content)
    ti.mtime = now
    ti.mode = 0o644
    ti.uname = 'root'
    ti.gname = 'root'
    tar.addfile(ti, io.BytesIO(ppd_content))

data_tar_gz = data_buf.getvalue()

# 4. Construct Debian ar archive
def ar_header(name, size, mode=0o100644, mtime=now):
    name_field = f"{name}/".ljust(16)
    mtime_field = str(mtime).ljust(12)
    uid_field = "0".ljust(6)
    gid_field = "0".ljust(6)
    mode_field = oct(mode)[2:].ljust(8)
    size_field = str(size).ljust(10)
    return (name_field + mtime_field + uid_field + gid_field + mode_field + size_field).encode('ascii') + b"`\n"

with open(deb_path, 'wb') as deb:
    deb.write(b"!<arch>\n")

    # debian-binary
    deb.write(ar_header("debian-binary", len(debian_binary)))
    deb.write(debian_binary)
    if len(debian_binary) % 2 == 1:
        deb.write(b"\n")

    # control.tar.gz
    deb.write(ar_header("control.tar.gz", len(control_tar_gz)))
    deb.write(control_tar_gz)
    if len(control_tar_gz) % 2 == 1:
        deb.write(b"\n")

    # data.tar.gz
    deb.write(ar_header("data.tar.gz", len(data_tar_gz)))
    deb.write(data_tar_gz)
    if len(data_tar_gz) % 2 == 1:
        deb.write(b"\n")

print(f"Successfully generated {deb_path} ({os.path.getsize(deb_path)} bytes)")