package main

import (
	"context"
	"fmt"
	"os"

	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/client"
	"github.com/spf13/cobra"
)

func main() {
	// Create the root command
	var rootCmd = &cobra.Command{
		Use:   "etl_pipeline",
		Short: "CLI for managing the etl pipeline",
	}

	// Create the list command
	var listCmd = &cobra.Command{
		Use:   "list-containers",
		Short: "List all running docker containers",
		RunE: func(cmd *cobra.Command, args []string) error {
			return ListContainer()
		},
	}

	// Add the list command to the root command
	rootCmd.AddCommand(listCmd)

	// Execute the root command
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func ListContainer() error {
	// Create Docker client with API version negotiation
	cli, err := client.NewClientWithOpts(client.WithAPIVersionNegotiation())
	if err != nil {
		return fmt.Errorf("failed to create Docker client: %w", err)
	}
	defer cli.Close()

	containers, err := cli.ContainerList(context.Background(), container.ListOptions{})
	if err != nil {
		return fmt.Errorf("failed to list containers: %w", err)
	}

	if len(containers) > 0 {
		for _, container := range containers {
			fmt.Printf("%s %s (status: %s) %s\n", container.Names, container.Image, container.Status, container.Command)
			for _, port := range container.Ports {
				fmt.Printf("%s:%d -> %d, ", port.IP, port.PublicPort, port.PrivatePort)
			}
		}
	} else {
		fmt.Println("There are no containers running")
	}
	return nil
}
