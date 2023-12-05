package fr.aston.petsitting.entity;

import java.io.Serializable;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.Date;
import java.util.List;


/**
 * The persistent class for the animal database table.
 * 
 */
@Entity
@Table(name="animal")
public class AnimalEntity implements Serializable {
	private static final long serialVersionUID = 1L;

	@Id
	@GeneratedValue(strategy=GenerationType.IDENTITY)
	@Column(unique=true, nullable=false)
	private int id;

	@Column(length=45)
	private String breed;

	@Temporal(TemporalType.DATE)
	@Column(name="date_of_birth", nullable=false)
	private Date dateOfBirth;

	@Column(name="is_social", nullable=false)
	private byte isSocial;

	@Column(name="is_sterilized", nullable=false)
	private byte isSterilized;

	@Column(name="is_vaccinated", nullable=false)
	private byte isVaccinated;

	@Column(name="pet_name", nullable=false, length=45)
	private String petName;

	@Column(name="pet_photo", length=200)
	private String petPhoto;

	@Column(nullable=false, length=1)
	private SexEnum sex;

	@Column(nullable=false, precision=10, scale=2)
	private BigDecimal weight;

	//bi-directional many-to-one association to UserEntity
	@ManyToOne
	@JoinColumn(name="user_id", nullable=false)
	private UserEntity user;

	//bi-directional many-to-one association to BookingEntity
	@OneToMany(mappedBy="animal")
	private List<BookingEntity> bookings;

	public AnimalEntity() {
	}

	public int getId() {
		return this.id;
	}

	public void setId(int id) {
		this.id = id;
	}

	public String getBreed() {
		return this.breed;
	}

	public void setBreed(String breed) {
		this.breed = breed;
	}

	public Date getDateOfBirth() {
		return this.dateOfBirth;
	}

	public void setDateOfBirth(Date dateOfBirth) {
		this.dateOfBirth = dateOfBirth;
	}

	public byte getIsSocial() {
		return this.isSocial;
	}

	public void setIsSocial(byte isSocial) {
		this.isSocial = isSocial;
	}

	public byte getIsSterilized() {
		return this.isSterilized;
	}

	public void setIsSterilized(byte isSterilized) {
		this.isSterilized = isSterilized;
	}

	public byte getIsVaccinated() {
		return this.isVaccinated;
	}

	public void setIsVaccinated(byte isVaccinated) {
		this.isVaccinated = isVaccinated;
	}

	public String getPetName() {
		return this.petName;
	}

	public void setPetName(String petName) {
		this.petName = petName;
	}

	public String getPetPhoto() {
		return this.petPhoto;
	}

	public void setPetPhoto(String petPhoto) {
		this.petPhoto = petPhoto;
	}

	public SexEnum getSex() {
		return this.sex;
	}

	public void setSex(SexEnum sex) {
		this.sex = sex;
	}

	public BigDecimal getWeight() {
		return this.weight;
	}

	public void setWeight(BigDecimal weight) {
		this.weight = weight;
	}

	public UserEntity getUser() {
		return this.user;
	}

	public void setUser(UserEntity user) {
		this.user = user;
	}

	public List<BookingEntity> getBookings() {
		return this.bookings;
	}

	public void setBookings(List<BookingEntity> bookings) {
		this.bookings = bookings;
	}

	public BookingEntity addBooking(BookingEntity booking) {
		getBookings().add(booking);
		booking.setAnimal(this);

		return booking;
	}

	public BookingEntity removeBooking(BookingEntity booking) {
		getBookings().remove(booking);
		booking.setAnimal(null);

		return booking;
	}

}