"""Central declarative registry for service-specific handbook reader enhancements.

Adding a new service staffing/equipment reader enhancement only requires registering
it here (instead of duplicating imports, calls, counters, and count assertions across
rewrite_public_navigation.py and finalize_github_pages_site.py).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

if __package__:
    from .care_management_staffing_reader import add_care_management_staffing_overview
    from .care_medical_staffing_reader import (
        add_care_medical_staffing_overview,
        validate_facility_manager_law_sources,
    )
    from .community_facility_equipment_reader import add_community_facility_equipment_overview
    from .community_staffing_reader import add_community_staffing_overview
    from .dementia_dayservice_staffing_reader import add_dementia_dayservice_staffing_overview
    from .group_home_staffing_reader import add_group_home_staffing_overview
    from .health_facility_staffing_reader import add_health_facility_staffing_overview
    from .homebath_staffing_reader import add_homebath_staffing_overview
    from .night_homevisit_manager_clarification import clarify_night_homevisit_manager
    from .nursing_small_scale_roles_clarification import clarify_nursing_small_scale_roles
    from .preventive_dementia_dayservice_staffing_reader import (
        add_preventive_dementia_dayservice_staffing_overview,
    )
    from .preventive_group_home_staffing_reader import add_preventive_group_home_staffing_overview
    from .preventive_homebath_staffing_reader import add_preventive_homebath_staffing_overview
    from .welfare_facility_staffing_reader import (
        add_welfare_facility_staffing_overview,
        validate_welfare_facility_care_sources,
    )
else:
    from care_management_staffing_reader import add_care_management_staffing_overview
    from care_medical_staffing_reader import (
        add_care_medical_staffing_overview,
        validate_facility_manager_law_sources,
    )
    from community_facility_equipment_reader import add_community_facility_equipment_overview
    from community_staffing_reader import add_community_staffing_overview
    from dementia_dayservice_staffing_reader import add_dementia_dayservice_staffing_overview
    from group_home_staffing_reader import add_group_home_staffing_overview
    from health_facility_staffing_reader import add_health_facility_staffing_overview
    from homebath_staffing_reader import add_homebath_staffing_overview
    from night_homevisit_manager_clarification import clarify_night_homevisit_manager
    from nursing_small_scale_roles_clarification import clarify_nursing_small_scale_roles
    from preventive_dementia_dayservice_staffing_reader import (
        add_preventive_dementia_dayservice_staffing_overview,
    )
    from preventive_group_home_staffing_reader import add_preventive_group_home_staffing_overview
    from preventive_homebath_staffing_reader import add_preventive_homebath_staffing_overview
    from welfare_facility_staffing_reader import (
        add_welfare_facility_staffing_overview,
        validate_welfare_facility_care_sources,
    )


@dataclass(frozen=True)
class ReaderEnhancement:
    key: str
    transform: Callable[[str, Path], tuple[str, int]]
    expected_count: int = 1
    error_message: str | None = None

    def failure_message(self) -> str:
        return self.error_message or f"Missing or duplicate staffing overview: {self.key}"


SOURCE_VALIDATORS: tuple[Callable[[Path], None], ...] = (
    validate_welfare_facility_care_sources,
    validate_facility_manager_law_sources,
)

READER_ENHANCEMENTS: tuple[ReaderEnhancement, ...] = (
    ReaderEnhancement("community_staffing_overview", add_community_staffing_overview),
    ReaderEnhancement("health_facility_staffing_overview", add_health_facility_staffing_overview),
    ReaderEnhancement("welfare_facility_staffing_overview", add_welfare_facility_staffing_overview),
    ReaderEnhancement("group_home_staffing_overview", add_group_home_staffing_overview),
    ReaderEnhancement(
        "preventive_group_home_staffing_overview",
        add_preventive_group_home_staffing_overview,
    ),
    ReaderEnhancement("night_homevisit_manager", clarify_night_homevisit_manager),
    ReaderEnhancement("care_medical_staffing_overview", add_care_medical_staffing_overview),
    ReaderEnhancement("nursing_small_scale_roles", clarify_nursing_small_scale_roles),
    ReaderEnhancement("care_management_staffing_overview", add_care_management_staffing_overview),
    ReaderEnhancement(
        "dementia_dayservice_staffing_overview",
        add_dementia_dayservice_staffing_overview,
    ),
    ReaderEnhancement(
        "preventive_dementia_dayservice_staffing_overview",
        add_preventive_dementia_dayservice_staffing_overview,
    ),
    ReaderEnhancement(
        "homebath_staffing_overview",
        add_homebath_staffing_overview,
        expected_count=2,
        error_message="Missing or duplicate home-bathing staffing or operations source",
    ),
    ReaderEnhancement(
        "preventive_homebath_staffing_overview",
        add_preventive_homebath_staffing_overview,
        expected_count=2,
        error_message="Missing or duplicate preventive home-bathing staffing or operations source",
    ),
    ReaderEnhancement(
        "community_facility_equipment_overview",
        add_community_facility_equipment_overview,
    ),
)
