package fr.aston.petsitting.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import fr.aston.petsitting.entity.AnimalEntity;

@Repository
public interface IAnimalRepository extends JpaRepository<AnimalEntity, Integer> {

}
