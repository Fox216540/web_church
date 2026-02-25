from django.db import models
from urllib.parse import urlparse, parse_qs

# ------------------ Проповеди ------------------

class Sermon(models.Model):
	title = models.CharField("Название", max_length=255)
	description = models.TextField("Описание", blank=True)
	author = models.CharField("Проповедник", max_length=255)
	scripture = models.CharField("Место Писания", max_length=255, blank=True)  # <-- новое поле
	video_url = models.URLField("YouTube URL")
	date = models.DateField("Дата")

	class Meta:
		ordering = ["-date"]
		db_table = "проповеди"

	def __str__(self):
		return self.title

	@property
	def thumbnail(self):
		query = urlparse(self.video_url).query
		video_id = parse_qs(query).get("v", [""])[0]
		return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"


# ------------------ События ------------------

class Event(models.Model):
	name = models.CharField("Название", max_length=255)
	description = models.TextField("Описание", blank=True)

	date_start = models.DateField("Дата начала")
	time_start = models.TimeField("Время начала", blank=True, null=True)

	date_finish = models.DateField("Дата окончания", blank=True, null=True)
	time_finish = models.TimeField("Время окончания", blank=True, null=True)

	banner = models.ImageField("Баннер", upload_to="events/", blank=True, null=True)
	is_published = models.BooleanField("Опубликовано", default=True)

	class Meta:
		ordering = ["date_start", "time_start"]
		db_table = "события"

	def __str__(self):
		return self.name

	@property
	def has_time(self):
		return self.time_start is not None


# ------------------ Контент ------------------

class CategoryOfContent(models.Model):
	name = models.CharField("Название", max_length=255)
	slug = models.SlugField(unique=True)
	drive_url = models.URLField("Ссылка Google Drive", blank=True, null=True)

	class Meta:
		db_table = "категории_контента"

	def __str__(self):
		return self.name


class Content(models.Model):
	url = models.URLField("Google Drive URL")

	category = models.ForeignKey(
		CategoryOfContent,
		on_delete=models.CASCADE,
		related_name="contents",
	)

	drive_date = models.DateTimeField("Дата файла в Google Drive", db_index=True)

	class Meta:
		db_table = "контент"
		ordering = ["-drive_date"]

	def __str__(self):
		return f"{self.drive_date} — {self.url}"


# ------------------ Домашние группы ------------------

class HomeGroup(models.Model):
	leader = models.CharField("Лидер группы", max_length=255)
	photo_of_leader = models.ImageField(
		"Фото лидера",
		upload_to="home_groups/leaders/",
		blank=True,
		null=True,
	)
	location = models.CharField("Район / Место", max_length=255)
	meeting_time = models.CharField("Время встречи", max_length=100)

	class Meta:
		db_table = "домашние_группы"

	def __str__(self):
		return self.leader


# ------------------ Документы церкви ------------------

class ChurchDocumentType(models.Model):
	code = models.SlugField("Код", unique=True)
	name = models.CharField("Название", max_length=255)

	class Meta:
		db_table = "типы_документов_церкви"

	def __str__(self):
		return self.name


class ChurchDocument(models.Model):
	doc_type = models.ForeignKey(
		ChurchDocumentType,
		on_delete=models.PROTECT,
		related_name="documents",
	)

	slug = models.SlugField(unique=True)  # ← добавить
	title = models.CharField(max_length=255)
	content = models.TextField()
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		db_table = "документы_церкви"

	def __str__(self):
		return self.title

# ------------------ Контакты ------------------

class ContactItem(models.Model):
	title = models.CharField("Заголовок", max_length=100)
	value = models.TextField("Значение")
	link = models.CharField("Ссылка", max_length=255, blank=True, null=True)

	icon = models.CharField(
		"Иконка FontAwesome",
		max_length=50,
		default="fa-map-marker-alt"
	)

	order = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["order"]
	def __str__(self):
		return self.title
		
class ContactSettings(models.Model):
	map_embed = models.TextField("Google Maps embed iframe", blank=True)

	class Meta:
		db_table = "contact_settings"
# ------------------ Служения ------------------

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

	class Meta:
		db_table = "служения"

	def __str__(self):
		return self.name


# ------------------ Церковный совет ------------------

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
		db_table = "церковный_совет"

	def __str__(self):
		return f"{self.name} — {self.role}"


# ------------------ SEO ------------------

class SeoPage(models.Model):
	slug = models.SlugField(unique=True)
	title = models.CharField(max_length=255)
	description = models.TextField()

	class Meta:
		db_table = "seo_страницы"
