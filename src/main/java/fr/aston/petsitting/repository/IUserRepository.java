package fr.aston.petsitting.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import fr.aston.petsitting.entity.UserEntity;


@Repository
public interface IUserRepository 
	extends JpaRepository<UserEntity, Integer>{

}
