"""Transcript fetching functionality using yt-dlp."""

import json

import yt_dlp

from src.core.config import Settings, get_settings
from src.core.exceptions import TranscriptNotAvailableError
from src.core.logging import get_logger

logger = get_logger(__name__)


class TranscriptFetcher:
    """Handles fetching YouTube video transcripts using yt-dlp."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the transcript fetcher.

        Args:
            settings: Application settings (optional)
        """
        self.settings = settings or get_settings()

    def get_transcript(self, video_id: str, languages: list[str] | None = ['en']) -> str:
        """Get transcript for a video using yt-dlp.

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

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Configure yt-dlp options
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': languages,
            'subtitlesformat': 'json3',
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info
                info = ydl.extract_info(video_url, download=False)

                # Get available captions
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})

                # Try to find captions in preferred languages
                captions = None
                caption_lang = None

                # First try manual subtitles
                for lang in languages:
                    if lang in subtitles:
                        captions = subtitles[lang]
                        caption_lang = lang
                        logger.debug(f"Using manual subtitles ({lang}) for video {video_id}")
                        break

                if not captions:
                    for lang in languages:
                        if lang in automatic_captions:
                            captions = automatic_captions[lang]
                            caption_lang = lang
                            logger.debug(f"Using automatic captions ({lang}) for video {video_id}")
                            break

                # Try English as fallback
                if not captions and 'en' in automatic_captions:
                    captions = automatic_captions['en']
                    caption_lang = 'en'
                    logger.debug(f"Using automatic captions (fallback: en) for video {video_id}")

                if not captions:
                    raise TranscriptNotAvailableError(
                        f"No captions found for video {video_id}"
                    )

                # Find JSON3 format
                json3_caption = None
                for caption_format in captions:
                    if caption_format.get('ext') == 'json3':
                        json3_caption = caption_format
                        break

                if not json3_caption:
                    raise TranscriptNotAvailableError(
                        f"JSON3 caption format not available for video {video_id}"
                    )

                # Download and parse caption data
                caption_url = json3_caption['url']
                caption_data = ydl.urlopen(caption_url).read().decode('utf-8')
                caption_json = json.loads(caption_data)

                # Extract text from JSON
                transcript_parts = []
                events = caption_json.get('events', [])

                for event in events:
                    segs = event.get('segs')
                    if segs:
                        for seg in segs:
                            text = seg.get('utf8', '').strip()
                            if text:
                                transcript_parts.append(text)

                full_transcript = ' '.join(transcript_parts)

                if not full_transcript:
                    raise TranscriptNotAvailableError(
                        f"Transcript is empty for video {video_id}"
                    )

                logger.info(
                    f"Successfully fetched transcript for video {video_id} "
                    f"({len(full_transcript)} characters, language: {caption_lang})"
                )
                return full_transcript

        except TranscriptNotAvailableError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch transcript for video {video_id}: {e}")
            raise TranscriptNotAvailableError(
                f"Failed to fetch transcript for video {video_id}: {e}"
            )
