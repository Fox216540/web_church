import os
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List
import django
from dateutil.parser import parse
from logger import status_logger



def setup_django() -> None:
    """
    Initialize Django so standalone scripts can use ORM.
    """
    project_root = Path(__file__).resolve().parents[1] / "church"
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "church.settings")

    django.setup()


def get_category_folder_ids() -> List[str]:
    """
    Return non-empty Google Drive folder IDs from CategoryOfContent.category_id.
    """
    setup_django()
    from api.models import CategoryOfContent

    return list(
        CategoryOfContent.objects.exclude(category_id__isnull=True)
        .exclude(category_id__exact="")
        .values_list("category_id", flat=True)
        .distinct()
    )


def get_category_folders() -> List[Dict[str, str]]:
    """
    Return categories as [{'id': <folder_id>, 'name': <category_name>}, ...].
    """
    setup_django()
    from api.models import CategoryOfContent

    qs = (
        CategoryOfContent.objects.exclude(category_id__isnull=True)
        .exclude(category_id__exact="")
        .values("category_id", "name")
        .order_by("name")
    )

    folders = [{"id": row["category_id"], "name": row["name"]} for row in qs]
    status_logger.info("Loaded %s category folder mappings from DB", len(folders))
    return folders


def _normalize_drive_date(item: Dict[str, Any]) -> date:
    """
    Pick and normalize date from Drive payload.
    """
    raw_value = (
        item.get("drive_date")
        or item.get("date")
        or item.get("created_time")
        or item.get("first_seen_in_folder")
    )
    if not raw_value:
        return date.today()
    return parse(str(raw_value)).date()


def _get_category_by_folder_id(folder_id: str):
    from api.models import CategoryOfContent

    category = CategoryOfContent.objects.filter(category_id=folder_id).first()
    if not category:
        raise ValueError(f"CategoryOfContent not found for folder_id={folder_id}")
    return category


def _normalize_photo_input(photo: Dict[str, Any] | str) -> tuple[str, Dict[str, Any]]:
    if isinstance(photo, str):
        photo_id = photo.strip()
        return photo_id, {"id": photo_id}

    photo_payload = photo
    photo_id = str(photo.get("id") or photo.get("photo_id") or "").strip()
    return photo_id, photo_payload


def _save_single_photo(photo_payload: Dict[str, Any], photo_id: str, category) -> bool:
    from api.models import Content

    drive_date = _normalize_drive_date(photo_payload)
    _, created = Content.objects.update_or_create(
        photo_id=photo_id,
        defaults={
            "category": category,
            "drive_date": drive_date,
        },
    )
    return created


def save_photos_for_folder(folder_id: str, photos: List[Dict[str, Any] | str]) -> Dict[str, int]:
    """
    Save photos into Content for category mapped by CategoryOfContent.category_id.

    photo item can be:
    - {'id': 'photo_id', 'drive_date': '2026-02-28'}
    - {'photo_id': 'photo_id', 'created_time': '...'}
    - 'photo_id'
    """
    setup_django()
    from api.models import Content

    category = _get_category_by_folder_id(folder_id)

    created_count = 0
    updated_count = 0
    seen_photo_ids: set[str] = set()

    for photo in photos:
        photo_id, photo_payload = _normalize_photo_input(photo)
        if not photo_id:
            continue

        seen_photo_ids.add(photo_id)
        if _save_single_photo(photo_payload, photo_id, category):
            created_count += 1
        else:
            updated_count += 1

    delete_qs = Content.objects.filter(category=category)
    if seen_photo_ids:
        delete_qs = delete_qs.exclude(photo_id__in=seen_photo_ids)
    deleted_count, _ = delete_qs.delete()

    return {
        "created": created_count,
        "updated": updated_count,
        "deleted": deleted_count,
        "total": created_count + updated_count,
    }
