
package fr.aston.petsitting.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import fr.aston.petsitting.entity.BookingEntity;

@Repository
public interface IBookingRepository extends JpaRepository<BookingEntity, Integer> {

}
