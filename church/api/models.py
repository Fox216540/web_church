from django.db import models
from urllib.parse import urlparse, parse_qs

class Sermon(models.Model):
	title = models.CharField("Название", max_length=255)
	description = models.TextField("Описание", blank=True)
	author = models.CharField("Проповедник", max_length=255)
	video_url = models.URLField("YouTube URL")
	date = models.DateField("Дата")

	class Meta:
		ordering = ["-date"]

	def __str__(self):
		return self.title
	
	@property
	def thumbnail(self):
		query = urlparse(self.video_url).query
		video_id = parse_qs(query).get("v", [""])[0]
		return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

class Event(models.Model):
	name = models.CharField("Название", max_length=255)
	description = models.TextField("Описание", blank=True)
	date_start = models.DateTimeField("Начало")
	date_finish = models.DateTimeField("Окончание", blank=True, null=True)
	banner = models.ImageField("Баннер", upload_to="events/", blank=True, null=True)
	is_published = models.BooleanField("Опубликовано", default=True)

	class Meta:
		ordering = ["date_start"]

	def __str__(self):
		return self.name
	
class CategoryOfContent(models.Model):
	name = models.CharField("Название", max_length=255)
	slug = models.SlugField(unique=True)

	def __str__(self):
		return self.name


class Content(models.Model):
	title = models.CharField("Название", max_length=255)
	url = models.URLField("Ссылка")
	category = models.ForeignKey(
		CategoryOfContent,
		on_delete=models.CASCADE,
		related_name="contents"
	)

	def __str__(self):
		return self.title
	
class HomeGroup(models.Model):
	leader = models.CharField("Лидер группы", max_length=255)
	photo_of_leader = models.ImageField(
		"Фото лидера",
		upload_to="home_groups/leaders/",
		blank=True,
		null=True,
	)
	name = models.CharField("Название группы", max_length=255)
	location = models.CharField("Район / Место", max_length=255)
	meeting_time = models.CharField("Время встречи", max_length=100)

	def __str__(self):
		return self.name
	
class ChurchDocument(models.Model):
	TYPE_CHOICES = [
		("creed", "Символ веры"),
		("charter", "Устав"),
	]

	doc_type = models.CharField(
		"Тип документа",
		max_length=20,
		choices=TYPE_CHOICES,
		unique=True,
	)
	title = models.CharField("Заголовок", max_length=255)
	content = models.TextField("Текст документа")

	updated_at = models.DateTimeField("Обновлено", auto_now=True)

	def __str__(self):
		return self.get_doc_type_display()
	
	
class ChurchContact(models.Model):
	address = models.CharField("Адрес", max_length=255)
	phone = models.CharField("Телефон", max_length=50)
	email = models.EmailField()
	map_url = models.URLField("Google Maps")
	
class Ministry(models.Model):
	name = models.CharField("Название служения", max_length=255)
	description = models.TextField("Описание")
	leader = models.CharField("Ответственный")
	photo = models.ImageField(
		"Фото служения",
		upload_to="ministries/",
		blank=True,
		null=True,
	)

	phone = models.CharField("Телефон", max_length=50, blank=True)
	email = models.EmailField("Email", blank=True)
	telegram = models.URLField("Telegram", blank=True)
	whatsapp = models.URLField("WhatsApp", blank=True)
	instagram = models.URLField("Instagram", blank=True)

	def __str__(self):
		return self.name

class ChurchBoard(models.Model):
	name = models.CharField("Имя", max_length=255)
	role = models.CharField("Должность", max_length=255)
	photo = models.ImageField(
		"Фото",
		upload_to="church_board/",
		blank=True,
		null=True,
	)
	short_bio = models.TextField("Краткое описание", blank=True)

	phone = models.CharField("Телефон", max_length=50, blank=True)
	email = models.EmailField("Email", blank=True)
	telegram = models.URLField("Telegram", blank=True)

	order = models.PositiveIntegerField("Порядок", default=0)

	class Meta:
		ordering = ["order"]

	def __str__(self):
		return f"{self.name} — {self.role}"


class SeoPage(models.Model):
	slug = models.SlugField(unique=True)
	title = models.CharField(max_length=255)
	description = models.TextField()