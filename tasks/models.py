from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from taggit.models import Tag, TaggedItem
from django.template.defaultfilters import slugify
from unidecode import unidecode


class RuTag(Tag):
    class Meta:
        proxy = True

    def slugify(self, tag, i=None):
        return slugify(unidecode(self.name))[:128]


class RuTaggedItem(TaggedItem):
    class Meta:
        proxy = True

    @classmethod
    def tag_model(cls):
        return RuTag


class TodoItem(models.Model):
    tags = TaggableManager(through=RuTaggedItem)
    PRIORITY_HIGH = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_LOW = 3

    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, "Высокий приоритет"),
        (PRIORITY_MEDIUM, "Средний приоритет"),
        (PRIORITY_LOW, "Низкий приоритет"),
    ]

    description = models.CharField(max_length=64)
    is_completed = models.BooleanField("выполнено", default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks')

    priority = models.IntegerField(
        "Приоритет", choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM
    )

    def __str__(self):
        return self.description.lower()

    def get_absolute_url(self):
        return reverse("tasks:details", args=[self.pk])

    class Meta:
        ordering = ('-created',)


class TagCount(models.Model):
    tag_slug = models.CharField(max_length=128)
    tag_name = models.CharField(max_length=128)
    tag_id = models.PositiveIntegerField(default=0)
    tag_count = models.PositiveIntegerField(db_index=True, default=0)
