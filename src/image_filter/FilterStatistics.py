from dataclasses import dataclass, field
from typing import Dict, Set, List

@dataclass
class FilterStatistics:
    total_images: int = 0
    total_blurry_images: int = 0
    total_uniform_images: int = 0
    total_duplicate_images: int = 0
    total_filtered: Dict[str, int] = field(default_factory=dict)
    filtered_image_paths: Set[str] = field(default_factory=set)
    total_valid_images: int = 0
    num_of_errors: int = 0
    captured_errors: List[str] = field(default_factory=list)