from enrichment.schemas import CompanyProfile

EMPLOYEES_TO_SIZE = {
    "1-50": 2,
    "51-200": 4,
    "201-1000": 6,
    "1001-5000": 8,
    "5001+": 10,
    "unknown": 5
}

def calculate_company_size(
    profile: CompanyProfile
) -> int:
    return EMPLOYEES_TO_SIZE[
        profile.employee_range
    ]

CUSTOMER_TO_FIT = {
    "b2b_enterprise": 9,
    "developers": 8,
    "mixed": 6,
    "consumers": 3,
    "unknown": 5
}

def calculate_customer_fit(
    profile: CompanyProfile
)-> int:
    return CUSTOMER_TO_FIT [
        profile.customer_type
    ]

SIZE_POINTS = {
    "1-50": 1,
    "51-200": 2,
    "201-1000": 3,
    "1001-5000": 4,
    "5001+": 5,
    "unknown": 2
}

FUNDING_POINTS = {
    "public": 3,
    "late_stage": 2,
    "early_stage": 1,
    "unknown": 0
}

EVENT_POINTS = {
    "confirmed": 2,
    "not_found": 0,
    "unknown": 0
}

def calculate_sponsorship_potential(
    profile: CompanyProfile
) -> int:

    score = 1

    score += SIZE_POINTS[
        profile.employee_range
    ]

    score += FUNDING_POINTS[
        profile.public_or_funding
    ]

    score += EVENT_POINTS[
        profile.event_presence
    ]

    return min(score, 10)