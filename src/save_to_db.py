import os
import sqlite3

def db_save (db_name: str, filedir: str):
    cxn = sqlite3.connect(db_name);
    cxn_cursor = cxn.cursor()

    cxn_cursor.execute("CREATE TABLE IF NOT EXISTS records (word TEXT PRIMARY KEY, frames BLOB, hip_centers BLOB, shoulder_widths BLOB)", [])

    npy_dir = [d for d in os.listdir(filedir)]
    for d in npy_dir:
        files = os.listdir(os.path.join(filedir, d))
        hc_file = [f for f in files if f.endswith("_hc.npy")][0]
        sw_file = [f for f in files if f.endswith("_sw.npy")][0]
        fr_file = [f for f in files if f.endswith("_f.npy")][0]
        hcfile = open(os.path.join(filedir, d, hc_file), "rb")
        swfile = open(os.path.join(filedir, d, sw_file), "rb")
        frfile = open(os.path.join(filedir, d, fr_file), "rb")

        word = d.rsplit(".", 1)[0].lower().strip(".- ")
        cxn_cursor.execute ("INSERT OR REPLACE INTO records VALUES (?,?, ?, ?)", [word, frfile.read(), hcfile.read(), swfile.read()])
        hcfile.close()
        swfile.close()
        frfile.close()

    cxn.commit()
    cxn_cursor.execute("ANALYZE", []) # index
    cxn_cursor.execute("VACUUM", []) # compress and defrag
    cxn.close()
