package fr.aston.petsitting.repository;

import static org.junit.jupiter.api.Assertions.*;

import java.math.BigDecimal;
import java.util.Date;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import fr.aston.petsitting.entity.BookingEntity;

@SpringBootTest
class IBookingRepositoryTest {
	
	@Autowired
	private IBookingRepository repository;
	
	@Test
	void testInsert() throws Exception{
		BookingEntity entity = new BookingEntity();
				entity.setStartDate(new Date());
				entity.setEndDate(new Date());
				entity.setTotalPrice(BigDecimal.valueOf(345,32));
				
	}
}
