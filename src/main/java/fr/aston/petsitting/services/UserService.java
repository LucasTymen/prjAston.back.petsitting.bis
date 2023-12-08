package fr.aston.petsitting.services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import fr.aston.petsitting.entity.UserEntity;
import fr.aston.petsitting.repository.IUserRepository;

@Service
public class UserService {

	@Autowired
	private IUserRepository repository;

	public UserEntity getUserById(int id) {
		return this.repository.findById(id).get();
	}

}
