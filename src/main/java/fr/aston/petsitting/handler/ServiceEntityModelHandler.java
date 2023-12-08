package fr.aston.petsitting.handler;

import java.util.ArrayList;
import java.util.List;

import fr.aston.petsitting.entity.ServiceEntity;
import fr.aston.petsitting.modele.ServiceModele;

public class ServiceEntityModelHandler {

	public static ServiceModele createModelFromEntity(ServiceEntity serviceEntity) {
		ServiceModele serviceModele = new ServiceModele();
		serviceModele.setId(serviceEntity.getId());
		serviceModele.setDailyPrice(serviceEntity.getDailyPrice());
		serviceModele.setName(serviceEntity.getName());
		serviceModele.setDescription(serviceEntity.getDescription());
		serviceModele.setType(serviceEntity.getType());
		serviceModele.setUserId(serviceEntity.getUser().getId());
		return serviceModele;
	}

	public static List<ServiceModele> createListModelFromEntities(List<ServiceEntity> serviceEntities) {
		List<ServiceModele> listModele = new ArrayList<>();
		for (ServiceEntity se : serviceEntities) {
			listModele.add(ServiceEntityModelHandler.createModelFromEntity(se));
		}
		return listModele;

	}

}
