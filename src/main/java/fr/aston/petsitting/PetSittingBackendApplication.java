package fr.aston.petsitting;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class PetSittingBackendApplication {
	// on place les ici les @bean supplémentaires éventuels
	public static void main(String[] args) {
		SpringApplication.run(PetSittingBackendApplication.class, args);
	}

}
