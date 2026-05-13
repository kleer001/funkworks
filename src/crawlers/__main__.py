"""Entry point: python -m src.crawlers

Crawls all sources for the configured DCC and writes raw + digest files.
"""

import json
import logging

from src.config import load_config, load_dcc_config
from src.crawlers.crawl import crawl_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    config = load_config()
    dcc_config = load_dcc_config(config.dcc_config_path) if config.dcc_config_path else None

    if dcc_config:
        dcc_name = dcc_config.get("name", config.subreddit)
        sources = [s.get("name", s.get("type")) for s in dcc_config.get("sources", [])]
        logging.info("Crawling %s from %d sources: %s", dcc_name, len(sources), sources)
    else:
        logging.info("No DCC config found — crawling r/%s (Reddit only)", config.subreddit)

    digest, raw_path = crawl_all(config, dcc_config)
    print(json.dumps(digest, indent=2))
    print(f"\nRaw posts: {raw_path}", flush=True)


if __name__ == "__main__":
    main()
