package fr.aston.petsitting.repository;

import java.math.BigDecimal;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import fr.aston.petsitting.entity.ServiceEntity;
import fr.aston.petsitting.entity.ServiceEnum;
import fr.aston.petsitting.entity.UserEntity;

@SpringBootTest
class IServiceRepositoryTest {

	@Autowired
	private IServiceRepository repository;

	@Autowired
	private IUserRepository userRepository;

	@Test
	void testInsert() throws Exception {
		ServiceEntity entity = new ServiceEntity();
		UserEntity user = this.userRepository.findById(1).get();

		entity.setDailyPrice(BigDecimal.valueOf(5));
		entity.setDescription("ma description test");
		entity.setName("mon service");
		entity.setType(ServiceEnum.WALK);
		entity.setUser(user);

		ServiceEntity entityInseree = this.repository.save(entity);
		Assertions.assertNotNull(entityInseree, "l'entite retournée doit exister");
		Assertions.assertTrue(entityInseree.getId() > 0, "l Id doit exister");

	}
}
