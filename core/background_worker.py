"""
core/background_worker.py
Asynchronous Background Ingestion Worker for SovereignCore
==========================================================
For Core and Prime tiers: periodically monitors user high-priority topics
(e.g., course syllabus updates, NVIDIA AI papers, stock indices),
pulls fresh knowledge from Tavily MCP, and proactively caches to SQLite.
"""

import threading
import time
from datetime import datetime
from typing import List, Dict
from core.tavily_search import TavilyMCPSearch
from core.vault import save_search, DB_PATH
import sqlite3


DEFAULT_WATCHLIST = [
    "NVIDIA Nemotron open source model updates",
    "Nebius AI serverless token factory announcements",
    "Computer Science Lab curriculum exam deadlines"
]


class ProactiveIngestionWorker:
    """
    Background worker thread running autonomous intelligence ingestion.
    """

    def __init__(self, interval_seconds: int = 180):
        self.interval = interval_seconds
        self.watchlist: List[str] = list(DEFAULT_WATCHLIST)
        self.is_running = False
        self._thread = None
        self.tavily = TavilyMCPSearch()
        self.latest_updates: List[Dict] = []
        self._lock = threading.Lock()

    def add_topic(self, topic: str):
        with self._lock:
            if topic not in self.watchlist:
                self.watchlist.append(topic)

    def get_watchlist(self) -> List[str]:
        with self._lock:
            return list(self.watchlist)

    def get_latest_proactive_updates(self) -> List[Dict]:
        with self._lock:
            return list(self.latest_updates)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False

    def _run_loop(self):
        # Initial run slightly delayed to let the app start cleanly
        time.sleep(3)
        while self.is_running:
            try:
                for topic in self.get_watchlist():
                    if not self.is_running:
                        break
                    results = self.tavily.search(topic, max_results=2)
                    if results and results[0].get("title") != "Tavily not configured":
                        save_search(f"[PROACTIVE-AUTO] {topic}", results)
                        with self._lock:
                            self.latest_updates.insert(0, {
                                "topic": topic,
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                                "headline": results[0].get("title", ""),
                                "url": results[0].get("url", "")
                            })
                            # Keep last 15 updates
                            self.latest_updates = self.latest_updates[:15]
                    time.sleep(2)  # Avoid rate limit bursts between topics
            except Exception as e:
                print(f"[Worker Error] {e}")

            # Sleep interval
            for _ in range(self.interval):
                if not self.is_running:
                    break
                time.sleep(1)


# Global singleton worker instance
proactive_worker = ProactiveIngestionWorker()
