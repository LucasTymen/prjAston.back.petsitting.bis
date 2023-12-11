package fr.aston.petsitting.handler;

import java.util.ArrayList;
import java.util.List;

import fr.aston.petsitting.entity.BookingEntity;
import fr.aston.petsitting.entity.ServiceEntity;
import fr.aston.petsitting.modele.FindAllByDailyPriceBetweenOrTypeModelOut;

public class ServiceEntityModeleHandler {

	public static FindAllByDailyPriceBetweenOrTypeModelOut fromEntity(ServiceEntity serviceEntity) {
		FindAllByDailyPriceBetweenOrTypeModelOut resu = new FindAllByDailyPriceBetweenOrTypeModelOut();
		resu.setDailyPrice(serviceEntity.getDailyPrice());

		resu.setDescription(serviceEntity.getDescription());
		resu.setId(serviceEntity.getId());
		resu.setName(serviceEntity.getName());
		resu.setType(serviceEntity.getType());
		resu.setUserId(serviceEntity.getUser().getId());
		resu.setUserName(serviceEntity.getUser().getFirstName());
		List<BookingEntity> bookingEntities = serviceEntity.getBookings();

		if (bookingEntities != null && !bookingEntities.isEmpty()) {
			List<Integer> bookingIdies = new ArrayList<Integer>();
			for (BookingEntity e : bookingEntities) {
				bookingIdies.add(e.getId());
			}
			
			resu.setBookings(bookingIdies);
		}
	return resu;
	}

	public static List<FindAllByDailyPriceBetweenOrTypeModelOut> fromEntities (List<ServiceEntity> serviceEntities) {
		List<FindAllByDailyPriceBetweenOrTypeModelOut> resu = new ArrayList<FindAllByDailyPriceBetweenOrTypeModelOut>();
		for (ServiceEntity serviceEntity : serviceEntities) {
			resu.add(fromEntity(serviceEntity));		
		}
		return resu;
	}
}

