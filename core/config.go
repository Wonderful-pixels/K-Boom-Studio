package core

import (
	"fmt"

	"github.com/spf13/viper"
)

// Configurations exported
type CoreConfig struct {
	Server ServerConfig
	Player PlayerConfig
}

// ServerConfigurations exported
type ServerConfig struct {
	Port int
}

// DatabaseConfigurations exported
type PlayerConfig struct {
	SQPath string
}

func readConfig() {
	viper.SetConfigName("core_config")
	viper.AddConfigPath("configs")
	viper.SetConfigType("yml")

	var configuration CoreConfig
	if err := viper.ReadInConfig(); err != nil {
		fmt.Printf("Error reading config file, %s", err)
	}

	err := viper.Unmarshal(&configuration)
	if err != nil {
		fmt.Printf("Unable to decode into struct, %v", err)
	}

	fmt.Println("Core Server port is", configuration.Server.Port)
	fmt.Println("Core Player SQ Directory is", configuration.Player.SQPath)
	fmt.Println("Port is", viper.GetInt("server.port"))

}
