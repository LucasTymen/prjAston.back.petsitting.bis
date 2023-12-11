package fr.aston.petsitting.services;

import java.math.BigDecimal;
import java.util.List;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import fr.aston.petsitting.entity.ServiceEntity;
import fr.aston.petsitting.entity.ServiceEnum;
import fr.aston.petsitting.entity.UserEntity;
import fr.aston.petsitting.repository.IServiceRepository;
import fr.aston.petsitting.repository.IUserRepository;

@SpringBootTest
class ServiceSitterServiceTest {

	@Autowired
	private IServiceRepository monrepo;

	@Autowired
	private IUserRepository monUserRepository;

	@Test
	void testgetServicesByUserId() throws Exception {
		final int idUser = 1;

		ServiceEntity serviceEntity = new ServiceEntity();
		serviceEntity.setDailyPrice(BigDecimal.valueOf(34));
		serviceEntity.setType(ServiceEnum.WALK);
		serviceEntity.setDescription("ici, on teste la description du service");
		serviceEntity.setName("jojo");
		UserEntity user = monUserRepository.findById(idUser).get();
		serviceEntity.setUser(user);


		ServiceEntity serviceEntityInseree = this.monrepo.save(serviceEntity);

		int serviceEntityId = serviceEntityInseree.getId();
		List<ServiceEntity> lesServices = monrepo.findAllByUserId(idUser); 
		for (ServiceEntity e : lesServices) {
			if (e.getId() == serviceEntityId) {
				// ok
				return;
			}
		}
		Assertions.fail("Le service n'a pas ete trouve");		
		
	}
}
