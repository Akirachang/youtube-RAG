"""Transcript fetching functionality."""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from src.core.exceptions import TranscriptNotAvailableError
from src.core.logging import get_logger

logger = get_logger(__name__)


class TranscriptFetcher:
    """Handles fetching YouTube video transcripts."""
    youtube_transcript_api: YouTubeTranscriptApi
    def __init__(self) -> None:
        """Initialize the transcript fetcher."""
        self.youtube_transcript_api = YouTubeTranscriptApi()

    def get_transcript(self, video_id: str, languages: list[str] | None = None) -> str:
        """Get transcript for a video.

        Args:
            video_id: YouTube video ID
            languages: Preferred languages for transcript (default: ['en'])

        Returns:
            Video transcript as text

        Raises:
            TranscriptNotAvailableError: If transcript is not available
        """
        if languages is None:
            languages = ["en"]

        try:
            transcript_list = self.youtube_transcript_api.fetch(video_id=video_id)

            # Combine all text segments
            full_text = " ".join([entry.text for entry in transcript_list])

            logger.info(f"Successfully fetched transcript for video {video_id}")
            return full_text

        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
            logger.warning(f"Transcript not available for video {video_id}: {e}")
            raise TranscriptNotAvailableError(
                f"Transcript not available for video {video_id}: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching transcript for video {video_id}: {e}")
            raise TranscriptNotAvailableError(
                f"Failed to fetch transcript for video {video_id}: {e}"
            )
