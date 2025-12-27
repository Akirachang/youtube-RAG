"""Video fetching functionality."""

from typing import Any

from googleapiclient.errors import HttpError

from src.core.exceptions import YouTubeAPIError
from src.core.logging import get_logger

logger = get_logger(__name__)


class VideoFetcher:
    """Handles fetching YouTube videos from a channel."""

    def __init__(self, youtube_client: Any) -> None:
        """Initialize the video fetcher.

        Args:
            youtube_client: Google API YouTube client instance
        """
        self.youtube = youtube_client

    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> list[dict[str, Any]]:
        """Get videos from a channel.

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to fetch

        Returns:
            List of video information dictionaries

        Raises:
            YouTubeAPIError: If API error occurs
        """
        try:
            # First get the uploads playlist ID
            channel_request = self.youtube.channels().list(
                part="contentDetails", id=channel_id
            )
            channel_response = channel_request.execute()

            if not channel_response.get("items"):
                raise YouTubeAPIError(f"Channel not found: {channel_id}")

            # NOTE: Every Youtube Channel has a special "uploads" playlist that contains all the videos of a Youtuber. We can use this to get all videos.
            uploads_playlist_id = channel_response["items"][0]["contentDetails"][
                "relatedPlaylists"
            ]["uploads"]

            # Get videos from uploads playlist
            videos = []
            next_page_token = None

            while len(videos) < max_results:
                playlist_request = self.youtube.playlistItems().list(
                    part="contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token,
                )
                playlist_response = playlist_request.execute()

                video_ids = [
                    item["contentDetails"]["videoId"] for item in playlist_response["items"]
                ]

                # Get detailed video information
                if video_ids:
                    videos_request = self.youtube.videos().list(
                        part="snippet,contentDetails,statistics", id=",".join(video_ids)
                    )
                    videos_response = videos_request.execute()

                    for video in videos_response["items"]:
                        videos.append(
                            {
                                "video_id": video["id"],
                                "title": video["snippet"]["title"],
                                "description": video["snippet"]["description"],
                                "published_at": video["snippet"]["publishedAt"],
                                "duration": video["contentDetails"]["duration"],
                                "view_count": video["statistics"].get("viewCount", "0"),
                                "like_count": video["statistics"].get("likeCount", "0"),
                                "comment_count": video["statistics"].get("commentCount", "0"),
                            }
                        )

                next_page_token = playlist_response.get("nextPageToken")
                if not next_page_token:
                    break

            logger.info(f"Fetched {len(videos)} videos from channel {channel_id}")
            return videos

        except HttpError as e:
            logger.error(f"YouTube API error while fetching videos: {e}")
            raise YouTubeAPIError(f"Failed to fetch videos: {e}")
