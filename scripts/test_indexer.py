import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logging import get_logger, setup_logging
from src.services.indexing import IndexingService

# Setup logging
setup_logging()
logger = get_logger(__name__)


def main():
    channel_handle: str = "@TheDailyShow"
    max_videos: int = 1

    try:
        logger.info("Initializing indexing service...")
        indexing_service = IndexingService()

        logger.info(f"Starting to index channel: {channel_handle}")
        stats = indexing_service.index_channel(
            channel_handle=channel_handle,
            max_videos=max_videos,
        )

        # Print results
        print("\n" + "=" * 60)
        print("Indexing Complete!")
        print("=" * 60)
        print(f"Channel Name:      {stats['channel_name']}")
        print(f"Channel ID:        {stats['channel_id']}")
        print(f"Videos Indexed:    {stats['videos_indexed']}")
        print(f"Videos Skipped:    {stats['videos_skipped']}")
        print(f"Total Chunks:      {stats['total_chunks']}")
        print("=" * 60)
        print("\nYou can now ask questions about this channel's content!")
        print("Run the Gradio app with: python -m src.app")
        print()

    except KeyboardInterrupt:
        logger.info("Indexing interrupted by user")
        print("\nIndexing interrupted. Partial data may have been saved.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
