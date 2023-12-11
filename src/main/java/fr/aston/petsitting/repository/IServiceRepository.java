
package fr.aston.petsitting.repository;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import fr.aston.petsitting.entity.ServiceEntity;
import fr.aston.petsitting.entity.ServiceEnum;

@Repository
public interface IServiceRepository extends JpaRepository<ServiceEntity, Integer> {

	// @Query("FROM ServiceEntity WHERE user.id = :userid ")
	// public List<ServiceEntity> getServicesByUserId(@Param("userid") int userId);

	// au lieu d'utiliser une méthode query ===> on peut utiliser les mots clefs
	public List<ServiceEntity> findAllByUserId(int userId);

	public List<ServiceEntity> findAllByDailyPriceBetweenAndType(BigDecimal minPrice, BigDecimal maxPrice,
			ServiceEnum type);

}
