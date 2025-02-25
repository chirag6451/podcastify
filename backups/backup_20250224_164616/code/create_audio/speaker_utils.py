"""Module for managing speaker configurations and selection."""
import json
from typing import List, Dict, Tuple

class Speaker:
    def __init__(self, name: str, voice_id: str, gender: str, accent: str, best_languages: List[str], personality: Dict, ideal_for: List[str]):
        self.name = name
        self.voice_id = voice_id
        self.gender = gender
        self.accent = accent
        self.best_languages = best_languages
        self.personality = personality
        self.ideal_for = ideal_for
    
    @property
    def personality_description(self) -> str:
        """Get a formatted description of the personality for prompts"""
        traits = ", ".join(self.personality["traits"])
        return f"{traits} with {self.personality['speaking_style']} speaking style"
    
    @property
    def language_description(self) -> str:
        """Get a formatted description of the speaker's languages"""
        return f"{self.accent} accent, fluent in {', '.join(self.best_languages)}"

def load_speakers() -> List[Speaker]:
    """Load speaker configurations from JSON file"""
    with open("speakers.json", "r") as f:
        data = json.load(f)
    
    return [
        Speaker(
            name=s["name"],
            voice_id=s["voice_id"],
            gender=s["gender"],
            accent=s["accent"],
            best_languages=s["best_languages"],
            personality=s["personality"],
            ideal_for=s["ideal_for"]
        )
        for s in data["speakers"]
    ]

def select_speakers_for_topic(topic: str, mood: str) -> List[Speaker]:
    """Select appropriate speakers based on topic and mood"""
    all_speakers = load_speakers()
    
    # Convert topic and mood to lowercase for matching
    topic_lower = topic.lower()
    mood_lower = mood.lower()
    
    # Score each speaker based on their suitability
    speaker_scores: List[Tuple[int, int, Speaker]] = []  # (score, index, speaker)
    for i, speaker in enumerate(all_speakers):
        score = 0
        # Check ideal_for matches
        for ideal in speaker.ideal_for:
            if ideal.lower() in topic_lower or ideal.lower() in mood_lower:
                score += 1
        speaker_scores.append((score, i, speaker))  # Include index for stable sorting
    
    # Sort by score (and index for stability) and get top 2 speakers
    speaker_scores.sort(key=lambda x: (-x[0], x[1]))  # Sort by -score (descending) then index (ascending)
    selected_speakers = [s[2] for s in speaker_scores[:2]]
    
    # If we couldn't find good matches, return first two speakers
    if len(selected_speakers) < 2:
        selected_speakers = all_speakers[:2]
    
    return selected_speakers

def get_voice_id(speaker_name: str, speakers: List[Speaker]) -> str:
    """Get the correct voice ID for a speaker"""
    for speaker in speakers:
        if speaker.name == speaker_name:
            return speaker.voice_id
    raise ValueError(f"No voice ID found for speaker {speaker_name}")
