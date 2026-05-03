package todo

import (
    "os"
    "testing"

    "github.com/example/todo-cli/internal/storage"
)

func TestServiceAddListCompleteDelete(t *testing.T) {
    // temp file for storage
    f, err := os.CreateTemp("", "todo_test_*.json")
    if err != nil {
        t.Fatalf("create temp file: %v", err)
    }
    path := f.Name()
    f.Close()
    defer os.Remove(path)

    fs := storage.NewFileStorage(path)
    svc := NewService(fs)

    id, err := svc.Add("test item", "", "high")
    if err != nil {
        t.Fatalf("Add failed: %v", err)
    }
    if id <= 0 {
        t.Fatalf("unexpected id: %d", id)
    }

    items, err := svc.List()
    if err != nil {
        t.Fatalf("List failed: %v", err)
    }
    if len(items) != 1 {
        t.Fatalf("expected 1 item, got %d", len(items))
    }

    if err := svc.Complete(id); err != nil {
        t.Fatalf("Complete failed: %v", err)
    }
    items, _ = svc.List()
    if !items[0].Completed {
        t.Fatalf("expected completed=true")
    }

    if err := svc.Delete(id); err != nil {
        t.Fatalf("Delete failed: %v", err)
    }
    items, _ = svc.List()
    if len(items) != 0 {
        t.Fatalf("expected 0 items after delete, got %d", len(items))
    }
}
