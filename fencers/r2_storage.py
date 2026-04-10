import os
import re
import uuid
from typing import List, Dict
from urllib.parse import quote

from django.conf import settings


def _slug_part(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "unknown"


def _ext(filename: str) -> str:
    ext = os.path.splitext(filename or "")[1].lower()
    return ext if ext else ".jpg"


def r2_ready() -> bool:
    return bool(
        settings.R2_ENABLED
        and settings.R2_ACCESS_KEY_ID
        and settings.R2_SECRET_ACCESS_KEY
        and settings.R2_BUCKET_NAME
        and settings.R2_ENDPOINT_URL
    )


def get_r2_client():
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def build_event_photo_key(event, subalbum, owner_profile, original_name: str) -> str:
    event_part = f"{event.id}-{_slug_part(event.title)}"
    owner_name = owner_profile.get_full_name() if owner_profile else ""
    owner_part = f"{owner_profile.id if owner_profile else 'unknown'}-{_slug_part(owner_name)}"
    subalbum_part = f"{subalbum.id}-{_slug_part(subalbum.name)}"
    file_part = f"{uuid.uuid4().hex}{_ext(original_name)}"
    return f"event_photos/{event_part}/{owner_part}/{subalbum_part}/{file_part}"


def build_object_url(object_key: str) -> str:
    if settings.R2_PUBLIC_BASE_URL:
        return f"{settings.R2_PUBLIC_BASE_URL.rstrip('/')}/{quote(object_key)}"
    endpoint = settings.R2_ENDPOINT_URL.rstrip("/")
    bucket = settings.R2_BUCKET_NAME
    return f"{endpoint}/{bucket}/{quote(object_key)}"


def upload_image_to_r2(*, file_obj, object_key: str, content_type: str = "") -> None:
    client = get_r2_client()
    params = {
        "Bucket": settings.R2_BUCKET_NAME,
        "Key": object_key,
        "Body": file_obj,
    }
    if content_type:
        params["ContentType"] = content_type
    client.put_object(**params)


def list_subalbum_images(*, event, subalbum, owner_profile) -> List[Dict[str, str]]:
    client = get_r2_client()
    event_part = f"{event.id}-{_slug_part(event.title)}"
    owner_name = owner_profile.get_full_name() if owner_profile else ""
    owner_part = f"{owner_profile.id if owner_profile else 'unknown'}-{_slug_part(owner_name)}"
    subalbum_part = f"{subalbum.id}-{_slug_part(subalbum.name)}"
    prefix = f"event_photos/{event_part}/{owner_part}/{subalbum_part}/"
    objects = []
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=settings.R2_BUCKET_NAME, Prefix=prefix):
        for item in page.get("Contents", []):
            key = item.get("Key")
            if not key:
                continue
            objects.append(
                {
                    "key": key,
                    "url": build_object_url(key),
                }
            )
    objects.sort(key=lambda x: x["key"], reverse=True)
    return objects


def safe_list_subalbum_images(*, event, subalbum, owner_profile) -> List[Dict[str, str]]:
    if not r2_ready():
        return []
    try:
        return list_subalbum_images(event=event, subalbum=subalbum, owner_profile=owner_profile)
    except Exception:
        return []

