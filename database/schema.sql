-- tabel users / pengguna
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    user_type TEXT NOT NULL CHECK(user_type IN ('Student', 'Teacher')),
    student_id TEXT UNIQUE,
    employee_id TEXT,
    class_name TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- tabel items / barang lab
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    total_stock INTEGER NOT NULL CHECK(total_stock >= 0),
    available_stock INTEGER NOT NULL CHECK(available_stock >= 0),
    is_archived INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- tabel peminjaman
CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_code TEXT UNIQUE NOT NULL,
    responsible_id INTEGER NOT NULL,
    requested_by_id INTEGER,
    collected_by_id INTEGER NOT NULL,
    loan_date TEXT NOT NULL,
    due_date TEXT,
    status TEXT DEFAULT 'Dipinjam',
    notes TEXT,
    FOREIGN KEY (responsible_id) REFERENCES users (id),
    FOREIGN KEY (requested_by_id) REFERENCES users (id),
    FOREIGN KEY (collected_by_id) REFERENCES users (id)
);

-- detail barang yg dipinjam
CREATE TABLE IF NOT EXISTS loan_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity_borrowed INTEGER NOT NULL,
    FOREIGN KEY (loan_id) REFERENCES loans (id),
    FOREIGN KEY (item_id) REFERENCES items (id)
);

-- tabel pengembalian
CREATE TABLE IF NOT EXISTS returns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    returner_id INTEGER NOT NULL,
    return_date TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (loan_id) REFERENCES loans (id),
    FOREIGN KEY (returner_id) REFERENCES users (id)
);

-- detail barang yg dikembalikan
CREATE TABLE IF NOT EXISTS return_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_id INTEGER NOT NULL,
    loan_detail_id INTEGER NOT NULL,
    quantity_returned INTEGER NOT NULL,
    condition TEXT DEFAULT 'Baik',
    notes TEXT,
    FOREIGN KEY (return_id) REFERENCES returns (id),
    FOREIGN KEY (loan_detail_id) REFERENCES loan_details (id)
);