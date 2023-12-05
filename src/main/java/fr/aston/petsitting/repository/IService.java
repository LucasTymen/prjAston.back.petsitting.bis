package fr.aston.petsitting.repository;


import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import fr.aston.petsitting.entity.ServiceEntity;

@Repository
public interface IService extends JpaRepository<ServiceEntity, Integer>{

}
