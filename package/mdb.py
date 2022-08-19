import pypyodbc
import shutil
from datetime import datetime


def makeMdbFile():

    try:
        conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=./mdb/HTZtables.mdb;')
        cursor = conn.cursor()
            
        cursor.execute('DELETE FROM STATIONX64')
        cursor.commit()

    except Exception as e:
        print(e)

    finally:
        cursor.close()
        conn.close()
    