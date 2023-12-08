package fr.aston.petsitting.controler;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import fr.aston.petsitting.entity.ServiceEntity;
import fr.aston.petsitting.handler.ServiceEntityModelHandler;
import fr.aston.petsitting.modele.ServiceModele;
import fr.aston.petsitting.services.ServiceSitterService;

@RestController
@RequestMapping("/sitterservice")
public class SitterServiceControler {

	@Autowired
	private ServiceSitterService service;

	@GetMapping("/list/{idUser}")
	public ResponseEntity<List<ServiceModele>> getSitterServiceListControler(@PathVariable("idUser") int idUser) {
		List<ServiceEntity> resultat = this.service.getServicesByUserId(idUser);
		List<ServiceModele> resultatModel = ServiceEntityModelHandler.createListModelFromEntities(resultat);
		return ResponseEntity.ok(resultatModel);
	}

}
