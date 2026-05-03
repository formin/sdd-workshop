package main

import (
    "fmt"
    "os"

    "github.com/spf13/cobra"
    "github.com/example/todo-cli/internal/storage"
    "github.com/example/todo-cli/internal/todo"
)

var service *todo.Service

func main() {
    var storageType string
    var dbPath string
    var filePath string

    var rootCmd = &cobra.Command{
        Use:   "todo",
        Short: "Simple ToDo CLI",
    }

    rootCmd.PersistentFlags().StringVar(&storageType, "storage", "file", "Storage backend: file|sqlite")
    rootCmd.PersistentFlags().StringVar(&dbPath, "db", "todo.db", "SQLite DB path")
    rootCmd.PersistentFlags().StringVar(&filePath, "file", "todo.json", "File storage path")

    // Initialize service before any command runs
    rootCmd.PersistentPreRunE = func(cmd *cobra.Command, args []string) error {
        if service != nil {
            return nil
        }
        if storageType == "sqlite" {
            s, err := storage.NewSQLiteStorage(dbPath)
            if err != nil {
                return err
            }
            service = todo.NewService(s)
            return nil
        }
        service = todo.NewService(storage.NewFileStorage(filePath))
        return nil
    }

    rootCmd.AddCommand(cmdAdd())
    rootCmd.AddCommand(cmdList())
    rootCmd.AddCommand(cmdComplete())
    rootCmd.AddCommand(cmdDelete())

    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}
