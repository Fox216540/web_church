from django.contrib import admin
from .models import (
	Sermon,
	Event,
	Content,
	CategoryOfContent,
	HomeGroup,
	ChurchDocument,
	ChurchDocumentType,
	Ministry,
	ContactItem,
	ContactSettings,
	ChurchBoard
)

admin.site.register(Sermon)
admin.site.register(Event)
admin.site.register(Content)
admin.site.register(CategoryOfContent)
admin.site.register(HomeGroup)
admin.site.register(ChurchDocument)
admin.site.register(Ministry)
admin.site.register(ContactItem)
admin.site.register(ContactSettings)
admin.site.register(ChurchDocumentType)
admin.site.register(ChurchBoard)