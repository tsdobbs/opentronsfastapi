import sqlite3
import threading
from functools import wraps

# Setup sqlite3 lock
conn = sqlite3.connect("lock.db")
c = conn.cursor()
table_sql = """
BEGIN;
CREATE TABLE IF NOT EXISTS lock (
    lock_id INT PRIMARY KEY,
    lock_active BOOL NOT NULL DEFAULT false,
    locked_by TEXT NOT NULL DEFAULT ''
);
INSERT INTO lock(lock_id) VALUES (1) ON CONFLICT DO NOTHING;
UPDATE lock SET lock_active = false, locked_by='' WHERE lock_id=1;
COMMIT;
"""
c.executescript(table_sql)
conn.close()

# Robotic locks
def get_lock(locked_by):
    conn = sqlite3.connect("lock.db")
    c_lock = conn.cursor()
    c_lock.execute("SELECT lock_active, locked_by FROM lock WHERE lock_id=1")
    lock_state = c_lock.fetchone()

    if lock_state[0] == False:
        # Acquire the lock
        c_lock.execute("UPDATE lock SET lock_active = true, locked_by=? WHERE lock_id=1", (locked_by,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False # Fail to acquire the lock

def unlock():
    conn = sqlite3.connect("lock.db")
    c_lock = conn.cursor()
    c_lock.execute("UPDATE lock SET lock_active = false, locked_by='' WHERE lock_id=1")
    conn.commit()
    conn.close()


#Decorator that executes the function in a seperate thread
def threaded_execute(locked_by, msg = "Execution initiated", simulate = False):
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            lock = get_lock(locked_by)
            if lock == False:
                return {"Message": "App currently locked"}

            if simulate:
                try:
                    func(*args, simulate=True)
                except TypeError as e:
                    msg = "If function doesn't accept a simulate argument, it can't be simulated. " + str(e)
                    print(msg)
                    return {"Message": msg}
                except Exception as e:
                    print(e)
                    return {"Message": str(e)}

            threading.Thread(target=func, args=args).start()
            return {"Message": msg}
        return inner
    return outer