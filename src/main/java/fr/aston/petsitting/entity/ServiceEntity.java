package fr.aston.petsitting.entity;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.List;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Lob;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

/**
 * The persistent class for the service database table.
 *
 */
@Entity
@Table(name = "service")
public class ServiceEntity implements Serializable {
	private static final long serialVersionUID = 1L;

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	@Column(unique = true, nullable = false)
	private int id;

	@Column(name = "daily_price", nullable = false, precision = 10, scale = 2)
	private BigDecimal dailyPrice;

	@Lob
	@Column(nullable = false)
	private String description;

	@Column(nullable = false, length = 125)
	private String name;

	@Column(nullable = false)
	@Enumerated(EnumType.STRING)
	private ServiceEnum type;

	// bi-directional many-to-one association to BookingEntity
	@OneToMany(mappedBy = "service")
	private List<BookingEntity> bookings;

	// bi-directional many-to-one association to UserEntity
	@ManyToOne
	@JoinColumn(name = "user_id", nullable = false)
	private UserEntity user;

	public ServiceEntity() {
	}

	public int getId() {
		return this.id;
	}

	public void setId(int id) {
		this.id = id;
	}

	public BigDecimal getDailyPrice() {
		return this.dailyPrice;
	}

	public void setDailyPrice(BigDecimal dailyPrice) {
		this.dailyPrice = dailyPrice;
	}

	public String getDescription() {
		return this.description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getName() {
		return this.name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public ServiceEnum getType() {
		return this.type;
	}

	public void setType(ServiceEnum type) {
		this.type = type;
	}

	public List<BookingEntity> getBookings() {
		return this.bookings;
	}

	public void setBookings(List<BookingEntity> bookings) {
		this.bookings = bookings;
	}

	public BookingEntity addBooking(BookingEntity booking) {
		this.getBookings().add(booking);
		booking.setService(this);

		return booking;
	}

	public BookingEntity removeBooking(BookingEntity booking) {
		this.getBookings().remove(booking);
		booking.setService(null);

		return booking;
	}

	public UserEntity getUser() {
		return this.user;
	}

	public void setUser(UserEntity user) {
		this.user = user;
	}

}