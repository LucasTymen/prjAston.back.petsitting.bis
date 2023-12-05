package fr.aston.petsitting.repository;

import static org.junit.jupiter.api.Assertions.*;

import java.math.BigDecimal;
import java.util.Date;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import fr.aston.petsitting.entity.AnimalEntity;
import fr.aston.petsitting.entity.BookingEntity;
import fr.aston.petsitting.entity.UserEntity;

@SpringBootTest
class IBookingRepositoryTest {

	@Autowired
	private IBookingRepository repository;
	
	@Autowired 
	private IAnimalRepository repository2;
	
	@Autowired 
	private IServiceRepository repository3;	


	@Test
	void testInsert() throws Exception {
		BookingEntity entity = new BookingEntity();
		entity.setStartDate(new Date());
		entity.setEndDate(new Date());
		entity.setTotalPrice(BigDecimal.valueOf(345, 32));
		entity.setAnimal(repository2.findById(1).get());
		entity.setService(repository3.findById(1).get());

		BookingEntity entityBooking = this.repository.save(entity);
		Assertions.assertNotNull(entityBooking, "L'entite retournee doit exister");
		Assertions.assertNotNull(entityBooking.getId() > 0, "L'ID doit exister");
	}
}
