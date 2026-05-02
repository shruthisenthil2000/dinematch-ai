"""Dataset identifiers and raw schema (contracts/dataset_contract.md)."""

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"

# Authoritative header order from dataset_contract.md
EXPECTED_RAW_COLUMNS = (
    "url",
    "address",
    "name",
    "online_order",
    "book_table",
    "rate",
    "votes",
    "phone",
    "location",
    "rest_type",
    "dish_liked",
    "cuisines",
    "approx_cost(for two people)",
    "reviews_list",
    "menu_item",
    "listed_in(type)",
    "listed_in(city)",
)

RAW_COST_COL = "approx_cost(for two people)"
RAW_CITY_COL = "listed_in(city)"
RAW_LOCALITY_COL = "location"
