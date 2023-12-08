package fr.aston.petsitting.modele;

import java.math.BigDecimal;

import fr.aston.petsitting.entity.ServiceEnum;

public class ServiceModele {

	private int id;
	private BigDecimal dailyPrice;
	private String description;
	private String name;
	private ServiceEnum type;
	private Integer userId;

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

	public Integer getUserId() {
		return this.userId;
	}

	public void setUserId(Integer userId) {
		this.userId = userId;
	}

}
