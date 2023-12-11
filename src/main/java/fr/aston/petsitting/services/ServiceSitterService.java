package fr.aston.petsitting.services;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import fr.aston.petsitting.entity.ServiceEntity;
import fr.aston.petsitting.entity.ServiceEnum;
import fr.aston.petsitting.repository.IServiceRepository;

@Service
public class ServiceSitterService {
	
	
	@Autowired
	private IServiceRepository repository; 
	
	public List<ServiceEntity> getServicesByUserId(int userId){
		return this.repository.findAllByUserId(userId);
		 
	}
	
	public List<ServiceEntity> findAllByServiceType(BigDecimal minPrice, BigDecimal maxPrice, ServiceEnum type){
		if(minPrice == null) {
			minPrice=BigDecimal.valueOf(0);
		}
		return this.repository.findAllByDailyPriceBetweenAndType(minPrice, maxPrice,type);
	}
	private void test (){
		
		
	}
public void testtt (){
		
		
	}

}