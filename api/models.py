
from django.db import models


# Certificates model for stock, signal, telecom
class Certificates(models.Model):
	stock = models.DateTimeField()
	signal = models.DateTimeField()
	telecom = models.DateTimeField()

	def __str__(self):
		return f"Stock: {self.stock}, Signal: {self.signal}, Telecom: {self.telecom}"

class Branding(models.Model):
	status = models.BooleanField()
	hours_remaining = models.IntegerField()
	total_hours = models.IntegerField(default=0)
	end_date = models.DateField(null=True, blank=True)

	def __str__(self):
		return f"Status: {self.status}, Hours: {self.hours_remaining}"


# Crew model
class Crew(models.Model):
	assigned = models.BooleanField()
	driver_id = models.CharField(max_length=32, null=True, blank=True)
	valid_until = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"Assigned: {self.assigned}, Driver: {self.driver_id}"

# Override model
class Override(models.Model):
	flag = models.BooleanField()
	category = models.CharField(max_length=64)
	reason = models.CharField(max_length=128)
	by = models.CharField(max_length=64)

	def __str__(self):
		return f"Override: {self.flag}, Category: {self.category}"

# Train model
class Train(models.Model):
	train_id = models.CharField(max_length=16, unique=True)
	depot_id = models.CharField(max_length=16, null=True, blank=True)
	certificates = models.OneToOneField(Certificates, on_delete=models.CASCADE, related_name='train', null=True, blank=True)
	branding = models.OneToOneField(Branding, on_delete=models.CASCADE, related_name='train', null=True, blank=True)
	cleaning_slot = models.BooleanField()
	crew = models.OneToOneField(Crew, on_delete=models.CASCADE, related_name='train', null=True, blank=True)
	override = models.OneToOneField(Override, on_delete=models.CASCADE, related_name='train', null=True, blank=True)
	mileage_odometer = models.IntegerField()
	mileage_last_service = models.DateField()
	service_status = models.CharField(max_length=32, null=True, blank=True)
	arrival_time = models.CharField(max_length=16, null=True, blank=True)

	def __str__(self):
		return self.train_id

class JobCard(models.Model):
	train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='jobcards')
	title = models.CharField(max_length=128)
	priority = models.CharField(max_length=32)

	def __str__(self):
		return f"{self.title} ({self.priority})"


# InductionList model
class InductionList(models.Model):
	train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='inductions')
	score = models.IntegerField()
	reason = models.CharField(max_length=256)
	override = models.BooleanField()
	violations = models.JSONField(default=list, blank=True)

	def __str__(self):
		return f"{self.train.train_id} ({self.score})"
