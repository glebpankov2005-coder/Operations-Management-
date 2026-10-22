"""
Convert Word files to PDF with LibreOffice and refresh the table of contents first (a plain 'soffice --convert-to pdf'
leaves the TOC field empty). Uses LibreOffice's own Python-UNO bridge, so run it with the system python3:
    python3 analysis/docx_to_pdf.py deliverables/portfolio/*.docx
"""
import os, subprocess, sys, time
import uno
from com.sun.star.beans import PropertyValue

PORT = 2002


def prop(name, value):
    p = PropertyValue(); p.Name = name; p.Value = value
    return p


def connect():
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(60):
        try:
            return resolver.resolve(f"uno:socket,host=127.0.0.1,port={PORT};urp;StarOffice.ComponentContext")
        except Exception:
            time.sleep(1)
    raise RuntimeError("LibreOffice did not start")


def main(paths):
    office = subprocess.Popen(["soffice", "--headless", "--invisible", "--nologo", "--norestore",
                               f"--accept=socket,host=127.0.0.1,port={PORT};urp;"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ctx = connect()
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        for path in paths:
            path = os.path.abspath(path)
            doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(path), "_blank", 0, (prop("Hidden", True),))
            idx = doc.getDocumentIndexes()
            for _ in range(2):                                   # second pass: page numbers after the TOC got its length
                for i in range(idx.getCount()):
                    idx.getByIndex(i).update()
            n_idx = idx.getCount()
            pdf = os.path.splitext(path)[0] + ".pdf"
            doc.storeToURL(uno.systemPathToFileUrl(pdf), (prop("FilterName", "writer_pdf_Export"),))
            doc.close(True)
            print(f"PDF ({n_idx} index updated): {pdf}")
    finally:
        try:
            desktop.terminate()
        except Exception:
            pass
        office.wait(timeout=60)


if __name__ == "__main__":
    main(sys.argv[1:])
