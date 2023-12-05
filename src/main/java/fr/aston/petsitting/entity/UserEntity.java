package fr.aston.petsitting.entity;

import java.io.Serializable;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.Date;
import java.util.List;


/**
 * The persistent class for the user database table.
 * 
 */
@Entity
@Table(name="user")
public class UserEntity implements Serializable {
	private static final long serialVersionUID = 1L;

	@Id
	@GeneratedValue(strategy=GenerationType.IDENTITY)
	@Column(unique=true, nullable=false)
	private int id;

	@Column(name="accomodation_type", length=1)
	private AccomodationTypeEnum accomodationType;

	@Column(nullable=false, length=200)
	private String address;

	@Column(nullable=false, length=45)
	private String city;

	@Temporal(TemporalType.DATE)
	@Column(name="date_of_birth", nullable=false)
	private Date dateOfBirth;

	@Column(nullable=false, length=125)
	private String email;

	@Column(name="first_name", nullable=false, length=45)
	private String firstName;

	@Column(name="has_garden")
	private byte hasGarden;

	@Column(name="has_vehicule")
	private byte hasVehicule;

	@Column(name="last_name", nullable=false, length=45)
	private String lastName;

	@Column(name="living_space", precision=10, scale=2)
	private BigDecimal livingSpace;

	@Column(nullable=false, length=45)
	private String password;

	@Column(nullable=false, length=45)
	private String pays;

	@Column(name="postal_code", nullable=false, length=10)
	private String postalCode;

	@Lob
	private String presentation;

	@Column(nullable=false, length=1)
	private RoleEnum role;

	@Column(length=1)
	private StatusEnum status;

	@Column(nullable=false, length=45)
	private String telephone;

	//bi-directional many-to-one association to AnimalEntity
	@OneToMany(mappedBy="user")
	private List<AnimalEntity> animals;

	//bi-directional many-to-one association to ServiceEntity
	@OneToMany(mappedBy="user")
	private List<ServiceEntity> services;

	public UserEntity() {
	}

	public int getId() {
		return this.id;
	}

	public void setId(int id) {
		this.id = id;
	}

	public AccomodationTypeEnum getAccomodationType() {
		return this.accomodationType;
	}

	public void setAccomodationType(AccomodationTypeEnum accomodationType) {
		this.accomodationType = accomodationType;
	}

	public String getAddress() {
		return this.address;
	}

	public void setAddress(String address) {
		this.address = address;
	}

	public String getCity() {
		return this.city;
	}

	public void setCity(String city) {
		this.city = city;
	}

	public Date getDateOfBirth() {
		return this.dateOfBirth;
	}

	public void setDateOfBirth(Date dateOfBirth) {
		this.dateOfBirth = dateOfBirth;
	}

	public String getEmail() {
		return this.email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public String getFirstName() {
		return this.firstName;
	}

	public void setFirstName(String firstName) {
		this.firstName = firstName;
	}

	public byte getHasGarden() {
		return this.hasGarden;
	}

	public void setHasGarden(byte hasGarden) {
		this.hasGarden = hasGarden;
	}

	public byte getHasVehicule() {
		return this.hasVehicule;
	}

	public void setHasVehicule(byte hasVehicule) {
		this.hasVehicule = hasVehicule;
	}

	public String getLastName() {
		return this.lastName;
	}

	public void setLastName(String lastName) {
		this.lastName = lastName;
	}

	public BigDecimal getLivingSpace() {
		return this.livingSpace;
	}

	public void setLivingSpace(BigDecimal livingSpace) {
		this.livingSpace = livingSpace;
	}

	public String getPassword() {
		return this.password;
	}

	public void setPassword(String password) {
		this.password = password;
	}

	public String getPays() {
		return this.pays;
	}

	public void setPays(String pays) {
		this.pays = pays;
	}

	public String getPostalCode() {
		return this.postalCode;
	}

	public void setPostalCode(String postalCode) {
		this.postalCode = postalCode;
	}

	public String getPresentation() {
		return this.presentation;
	}

	public void setPresentation(String presentation) {
		this.presentation = presentation;
	}

	public RoleEnum getRole() {
		return this.role;
	}

	public void setRole(RoleEnum role) {
		this.role = role;
	}

	public StatusEnum getStatus() {
		return this.status;
	}

	public void setStatus(StatusEnum status) {
		this.status = status;
	}

	public String getTelephone() {
		return this.telephone;
	}

	public void setTelephone(String telephone) {
		this.telephone = telephone;
	}

	public List<AnimalEntity> getAnimals() {
		return this.animals;
	}

	public void setAnimals(List<AnimalEntity> animals) {
		this.animals = animals;
	}

	public AnimalEntity addAnimal(AnimalEntity animal) {
		getAnimals().add(animal);
		animal.setUser(this);

		return animal;
	}

	public AnimalEntity removeAnimal(AnimalEntity animal) {
		getAnimals().remove(animal);
		animal.setUser(null);

		return animal;
	}

	public List<ServiceEntity> getServices() {
		return this.services;
	}

	public void setServices(List<ServiceEntity> services) {
		this.services = services;
	}

	public ServiceEntity addService(ServiceEntity service) {
		getServices().add(service);
		service.setUser(this);

		return service;
	}

	public ServiceEntity removeService(ServiceEntity service) {
		getServices().remove(service);
		service.setUser(null);

		return service;
	}

}