package main

import (
    "fmt"
    "strconv"

    "github.com/spf13/cobra"
)

func cmdAdd() *cobra.Command {
    var due string
    var priority string
    cmd := &cobra.Command{
        Use:   "add [title]",
        Short: "Add a new todo",
        Args:  cobra.MinimumNArgs(1),
        RunE: func(cmd *cobra.Command, args []string) error {
            title := args[0]
            id, err := service.Add(title, due, priority)
            if err != nil {
                return err
            }
            fmt.Printf("Created ID %d\n", id)
            return nil
        },
    }
    cmd.Flags().StringVar(&due, "due", "", "Due date (YYYY-MM-DD)")
    cmd.Flags().StringVar(&priority, "priority", "", "Priority: low|medium|high")
    return cmd
}

func cmdList() *cobra.Command {
    var show string
    cmd := &cobra.Command{
        Use:   "list",
        Short: "List todos",
        RunE: func(cmd *cobra.Command, args []string) error {
            items, err := service.List()
            if err != nil {
                return err
            }
            for _, it := range items {
                fmt.Printf("%d. [%v] %s (prio:%s) due:%s\n", it.ID, it.Completed, it.Title, it.Priority, it.DueDate)
            }
            return nil
        },
    }
    cmd.Flags().StringVar(&show, "show", "all", "Filter: all|completed|pending")
    return cmd
}

func cmdComplete() *cobra.Command {
    return &cobra.Command{
        Use:   "complete [id]",
        Short: "Mark todo complete",
        Args:  cobra.ExactArgs(1),
        RunE: func(cmd *cobra.Command, args []string) error {
            id, err := strconv.Atoi(args[0])
            if err != nil {
                return err
            }
            return service.Complete(id)
        },
    }
}

func cmdDelete() *cobra.Command {
    return &cobra.Command{
        Use:   "delete [id]",
        Short: "Delete todo",
        Args:  cobra.ExactArgs(1),
        RunE: func(cmd *cobra.Command, args []string) error {
            id, err := strconv.Atoi(args[0])
            if err != nil {
                return err
            }
            return service.Delete(id)
        },
    }
}
