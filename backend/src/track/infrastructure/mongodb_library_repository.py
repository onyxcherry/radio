def _get_data_from_database(self) -> Optional[dict]:
        from shared.database.connection import library

        # self._library_repository.get()
        result = library.find_one({"trackUrl": self._url})
        return result
    
    def get_status(self, track: Track) -> Status:
        data = self._get_data_from_database()
        if data is None:
            return Status.NOT_IN_LIBRARY

        database_status = data["status"]
        posibble_statuses = {
            status.value: Status[status.name] for status in Status
        }
        try:
            status = posibble_statuses[database_status]
        except KeyError:
            raise TrackLibraryUnknownStatus(
                f"Invalid status of track {repr(self)} "
                + f"in database: {database_status}"
            )
        else:
            return status
        
     def add_to_library_as_pending_to_approve(self) -> None:
        from shared.database.connection import library

        library.insert_one(
            {
                "trackUrl": self._url,
                "duration": self.get_duration(),
                "title": self.get_title(),
                "status": Status.PENDING_APPROVAL.value,
                "downloaded": False,
            }
        )

    def add_as_waiting_with_datetime_to_play(self, publish_datetime: datetime) -> None:
        from shared.database.connection import waiting
        from shared.database.query_utils import get_queue_weight_at

        waiting.insert_one(
            {
                "datetime": publish_datetime,
                "trackUrl": self._url,
                "weight": get_queue_weight_at(publish_datetime) + 1,
            }
        )
        logger.debug(f"Added {self} to waiting list at {publish_datetime}")

    def update_status(self, new_status: Status) -> None:
        from shared.database.connection import library
        self._library_repository.update()
        result = library.update_one(
            {"trackUrl": self._url}, {"$set": {"status": new_status.value}}
        )
        if result.matched_count == 1:
            logger.info(f"Updated track {self} status - set {new_status}")
        else:
            raise TrackStatusUpdateError(
                f"No track (with url: {self._url}) matched "
                + f" in an update command. Desired status: {new_status}"
            )
    def _check_track_duration_in_database(self) -> Optional[int]:
        result = self._get_data_from_database()
        if result and (duration := result.get("duration")):
            return int(duration)
        return None

    def _check_track_title_in_database(self) -> Optional[str]:
        result = self._get_data_from_database()
        if result and (title := result.get("title")):
            return title
        return None

def delete_from_queue_at(self, when: PlayingTime) -> int:
        from shared.database.connection import queue

        deleting_query = {
            "trackUrl": self._url,
            "datetime": {
                "$gte": publish_datetime,
                "$lte": publish_datetime + timedelta(minutes=1),
            },
        }
        deleted_count = queue.delete_one(deleting_query).deleted_count
        return int(deleted_count)

    def check_played_or_queued_at(self, when: PlayingTime) -> int:
        from shared.database.connection import history, queue

        search = {
            "trackUrl": self._url,
            "datetime": {
                "$gte": publish_datetime.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
                "$lte": publish_datetime.replace(
                    hour=23, minute=59, second=59, microsecond=999
                ),
            },
        }
        total_count = int(
            history.count_documents(search) + queue.count_documents(search)
        )
        return total_count

    def check_waiting_at(self, when: PlayingTime) -> bool:
        from shared.database.connection import waiting

        search = {
            "trackUrl": self._url,
            "datetime": {
                "$gte": publish_datetime.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
                "$lte": publish_datetime.replace(
                    hour=23, minute=59, second=59, microsecond=999
                ),
            },
        }
        count = int(waiting.count_documents(search))
        return bool(count)

    def add_to_queue_at(self, when: PlayingTime) -> None:
        from shared.database.connection import queue
        from shared.database.query_utils import get_queue_weight_at

        queue.insert_one(
            {
                "datetime": publish_datetime,
                "trackUrl": self._url,
                "weight": get_queue_weight_at(publish_datetime) + 1,
            }
        )
     def add_to_playing_history_at(self, play_datetime: datetime) -> None:
        from shared.database.connection import history

        played_track = {
            "trackUrl": self._url,
            "datetime": play_datetime,
        }
        history.insert_one(played_track)