"""
Houses code used across multiple apps.
"""
import uuid

from django.db import models


class BaseModel(models.Model):
    """Base class for all models."""

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, editable=False)
    updated_at = models.DateTimeField(
        auto_now=True, db_index=True, editable=False)

    class Meta:
        """Define a default least recently used ordering."""

        abstract = True
        ordering = ("-updated", "-created")
