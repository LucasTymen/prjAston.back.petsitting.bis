package fr.aston.petsitting.modele;

import java.math.BigDecimal;
import java.util.List;

import fr.aston.petsitting.entity.ServiceEnum;

/**
 * Objet qui SORT sur le controlleur
 */
public class FindAllByDailyPriceBetweenOrTypeModelOut {
	private int id;
	private BigDecimal dailyPrice;
	private String description;
	private String name;
	private ServiceEnum type;
	private List<Integer> bookings;
	private Integer userId;
	private String userName;
	
	public int getId() {
		return id;
	}
	public void setId(int id) {
		this.id = id;
	}
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public List<Integer> getBookings() {
		return bookings;
	}
	public void setBookings(List<Integer> bookings) {
		this.bookings = bookings;
	}
	public Integer getUserId() {
		return userId;
	}
	public void setUserId(Integer userId) {
		this.userId = userId;
	}
	public String getUserName() {
		return userName;
	}
	public void setUserName(String userName) {
		this.userName = userName;
	}	
	
	public BigDecimal getDailyPrice() {
		return dailyPrice;
	}
	public void setDailyPrice(BigDecimal dailyPrice) {
		this.dailyPrice = dailyPrice;
	}
	public ServiceEnum getType() {
		return type;
	}
	public void setType(ServiceEnum type) {
		this.type = type;
	}


}
