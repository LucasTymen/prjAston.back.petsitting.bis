package fr.aston.petsitting.controler;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import fr.aston.petsitting.entity.ServiceEntity;
import fr.aston.petsitting.handler.ServiceEntityModeleHandler;
import fr.aston.petsitting.modele.FindAllByDailyPriceBetweenOrTypeModelIn;
import fr.aston.petsitting.modele.FindAllByDailyPriceBetweenOrTypeModelOut;
import fr.aston.petsitting.services.ServiceSitterService;

@RestController
@RequestMapping("/servicesitterservicelist")
public class FindAllByDailyPriceBetweenOrTypeController {
	@Autowired
	private ServiceSitterService service;


	// <!-- http://localhost:8080/servicesitterservicelist/recuperer/VISIT =>
	// PathVariable -->
	// <!--
	// http://localhost:8080/servicesitterservicelist/recuperer?type=VISIT&pMin=0&pMax=55
	// => RequestParam -->
	// <!-- http://localhost:8080/servicesitterservicelist/sending/ avec du Json
	// dans le body => RequestBody => PAS possible en get -->

	@PostMapping("/sending")
	public ResponseEntity<List<FindAllByDailyPriceBetweenOrTypeModelOut>> sending(
			@RequestBody FindAllByDailyPriceBetweenOrTypeModelIn obj) {
		List<ServiceEntity> resu = service.findAllByServiceType(BigDecimal.valueOf(obj.getDailyPriceMin()),
				BigDecimal.valueOf(obj.getDailyPriceMax()), obj.getType());
		List<FindAllByDailyPriceBetweenOrTypeModelOut> resubis = ServiceEntityModeleHandler.fromEntities(resu);
		return ResponseEntity.ok(resubis);
	}
}
