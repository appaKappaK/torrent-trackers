import re
import json  
from typing import List
from models.tracker_models import Tracker
import logging

logger = logging.getLogger(__name__)

class TrackerParser:
    """Handles tracker parsing and duplicate detection"""
    
    @staticmethod
    def extract_trackers_from_text(text: str) -> List[str]:
        """Extract tracker URLs from text"""
        url_pattern = r'\b(https?://[^\s<>"{}|\\^`\[\]]+|udp://[^\s<>"{}|\\^`\[\]]+|magnet:\?[^\s<>"{}|\\^`\[\]]+)\b'
        matches = re.findall(url_pattern, text)
        return [match.strip() for match in matches if match.strip()]
    
    @staticmethod
    def remove_duplicates(trackers: List[str]) -> List[str]:
        """Remove duplicate trackers"""
        seen = set()
        unique_trackers = []
        
        for tracker in trackers:
            normalized = Tracker.normalize_tracker_url(tracker)
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_trackers.append(tracker)
        
        logger.info(f"Removed duplicates: {len(trackers)} -> {len(unique_trackers)}")
        return unique_trackers

    @staticmethod
    def parse_multiple_formats(content: str, format_type: str = 'auto') -> List[str]:
        """Parse tracker lists from different formats"""
        if format_type == 'auto':
            # Auto-detect format
            if content.strip().startswith('['):
                format_type = 'json'
            elif '\n' in content and ',' in content:
                format_type = 'csv'
            else:
                format_type = 'txt'
        
        if format_type == 'json':
            return TrackerParser.parse_json(content)
        elif format_type == 'csv':
            return TrackerParser.parse_csv(content)
        else:  # txt
            return TrackerParser.extract_trackers_from_text(content)

    @staticmethod
    def parse_json(content: str) -> List[str]:
        """Parse JSON tracker list"""
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return [str(item) for item in data if isinstance(item, str)]
            elif isinstance(data, dict) and 'trackers' in data:
                return [str(tracker) for tracker in data['trackers']]
            return []
        except json.JSONDecodeError:
            return []

    @staticmethod  
    def parse_csv(content: str) -> List[str]:
        """Parse CSV tracker list"""
        try:
            import csv
            reader = csv.reader(content.splitlines())
            trackers = []
            for row in reader:
                if row and row[0]:
                    trackers.append(row[0].strip())
            return trackers
        except Exception:
            return []

    @staticmethod
    def filter_trackers(trackers: List[str], query: str) -> List[str]:
        """Filter trackers by search query"""
        if not query:
            return trackers
        query = query.lower()
        return [t for t in trackers if query in t.lower()]