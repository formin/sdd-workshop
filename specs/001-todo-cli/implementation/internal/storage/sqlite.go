package storage

import (
    "database/sql"
    "errors"
    "time"

    _ "github.com/mattn/go-sqlite3"

    "github.com/example/todo-cli/internal/todo"
)

type SQLiteStorage struct {
    db *sql.DB
}

func NewSQLiteStorage(path string) (*SQLiteStorage, error) {
    db, err := sql.Open("sqlite3", path)
    if err != nil { return nil, err }
    stm := `CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        due_date TEXT,
        priority TEXT,
        completed INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    );`
    if _, err := db.Exec(stm); err != nil { db.Close(); return nil, err }
    return &SQLiteStorage{db: db}, nil
}

func (s *SQLiteStorage) Save(item todo.ToDoItem) (int, error) {
    if s.db == nil { return 0, errors.New("db not initialized") }
    res, err := s.db.Exec(`INSERT INTO todos(title,due_date,priority,completed,created_at) VALUES(?,?,?,?,?)`,
        item.Title, item.DueDate, item.Priority, boolToInt(item.Completed), item.CreatedAt.Format(time.RFC3339))
    if err != nil { return 0, err }
    id, err := res.LastInsertId()
    return int(id), err
}

func (s *SQLiteStorage) List() ([]todo.ToDoItem, error) {
    if s.db == nil { return nil, errors.New("db not initialized") }
    rows, err := s.db.Query(`SELECT id,title,due_date,priority,completed,created_at FROM todos ORDER BY id`)
    if err != nil { return nil, err }
    defer rows.Close()
    var items []todo.ToDoItem
    for rows.Next() {
        var it todo.ToDoItem
        var createdAt string
        var completed int
        if err := rows.Scan(&it.ID, &it.Title, &it.DueDate, &it.Priority, &completed, &createdAt); err != nil {
            return nil, err
        }
        it.Completed = completed != 0
        t, err := time.Parse(time.RFC3339, createdAt)
        if err == nil { it.CreatedAt = t }
        items = append(items, it)
    }
    return items, nil
}

func (s *SQLiteStorage) Update(item todo.ToDoItem) error {
    if s.db == nil { return errors.New("db not initialized") }
    _, err := s.db.Exec(`UPDATE todos SET title=?, due_date=?, priority=?, completed=? WHERE id=?`,
        item.Title, item.DueDate, item.Priority, boolToInt(item.Completed), item.ID)
    return err
}

func (s *SQLiteStorage) Delete(id int) error {
    if s.db == nil { return errors.New("db not initialized") }
    res, err := s.db.Exec(`DELETE FROM todos WHERE id=?`, id)
    if err != nil { return err }
    cnt, err := res.RowsAffected()
    if err != nil { return err }
    if cnt == 0 { return sql.ErrNoRows }
    return nil
}

func boolToInt(b bool) int {
    if b { return 1 }
    return 0
}
