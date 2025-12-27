"""Scratch script to test youtube-transcript-api functionality."""

from youtube_transcript_api import YouTubeTranscriptApi


def main():
    video_id = "v-sCZN3FbR0"  # Example video ID
    youtube_api = YouTubeTranscriptApi()
    transcript = youtube_api.fetch(video_id=video_id)

    print(transcript)

main()