package fr.aston.petsitting.services;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import fr.aston.petsitting.entity.ServiceEntity;
import fr.aston.petsitting.repository.IServiceRepository;

@Service
public class ServiceSitterService {

	@Autowired
	private IServiceRepository repository;

	public List<ServiceEntity> getServicesByUserId(int userId) {
		return this.repository.findAllByUserId(userId);
	}

	public ServiceEntity createService(ServiceEntity serviceEntity) {
		return this.repository.save(serviceEntity);
	}

}
