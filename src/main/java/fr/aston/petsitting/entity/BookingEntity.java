package fr.aston.petsitting.entity;

import java.io.Serializable;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.security.Provider.Service;
import java.util.Date;


/**
 * The persistent class for the booking database table.
 * 
 */
@Entity
@Table(name="booking")
public class BookingEntity implements Serializable {
	private static final long serialVersionUID = 1L;

	@Id
	@GeneratedValue(strategy=GenerationType.IDENTITY)
	@Column(unique=true, nullable=false)
	private int id;

	@Temporal(TemporalType.DATE)
	@Column(name="end_date", nullable=false)
	private Date endDate;

	@Temporal(TemporalType.DATE)
	@Column(name="start_date", nullable=false)
	private Date startDate;

	@Column(name="total_price", nullable=false, precision=10, scale=2)
	private BigDecimal totalPrice;

	//bi-directional many-to-one association to AnimalEntity
	@ManyToOne
	@JoinColumn(name="animal_id", nullable=false)
	private AnimalEntity animal;

	//bi-directional many-to-one association to ServiceEntity
	@ManyToOne
	@JoinColumn(name="service_id", nullable=false)
	private ServiceEntity service;

	public BookingEntity() {
	}

	public int getId() {
		return this.id;
	}

	public void setId(int id) {
		this.id = id;
	}

	public Date getEndDate() {
		return this.endDate;
	}

	public void setEndDate(Date endDate) {
		this.endDate = endDate;
	}

	public Date getStartDate() {
		return this.startDate;
	}

	public void setStartDate(Date startDate) {
		this.startDate = startDate;
	}

	public BigDecimal getTotalPrice() {
		return this.totalPrice;
	}

	public void setTotalPrice(BigDecimal totalPrice) {
		this.totalPrice = totalPrice;
	}

	public AnimalEntity getAnimal() {
		return this.animal;
	}

	public void setAnimal(AnimalEntity animal) {
		this.animal = animal;
	}

	public ServiceEntity getService() {
		return this.service;}

	public void setService(ServiceEntity service) {
		this.service = service;
	}

}