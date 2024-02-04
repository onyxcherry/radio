def is_downloaded(self) -> bool:
    data = self._get_data_from_database()
    if data is None or not data["downloaded"]:
        return False
    return True

def get_paths(self) -> tuple[str, str]:
    downloaded_filename = f"{self.file_prefix}_{self._id}"
    converted_filename = f"{self.file_prefix}_{self._id}.wav"
    file_paths = get_paths_or_create_track_files(
        downloaded_filename, converted_filename
    )
    return file_paths

def mark_as_downloaded(self) -> int:
    from shared.database.connection import library

    result = library.update_one(
        {"trackUrl": self._url},
        {"$set": {"downloaded": True}},
    )
    return int(result.modified_count)

def unmark_as_downloaded(self) -> int:
    from shared.database.connection import library

    result = library.update_one(
        {"trackUrl": self._url},
        {"$set": {"downloaded": False}},
    )
    return int(result.modified_count)

def mark_manual_download_needed(self) -> int:
    from shared.database.connection import library

    result = library.update_one(
        {"trackUrl": self._url},
        {"$set": {"needsManualDownload": True}},
    )
    return int(result.modified_count)