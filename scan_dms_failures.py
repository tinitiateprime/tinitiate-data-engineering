def get_irc_census_report_by_id(
    last_first_name: str,
    filters: Optional[Union[FiltersEnvelope, dict]] = None,
    page: Optional[PaginationModel] = None,
    columns: Optional[List[str]] = None,
    sort: Optional[SortModel] = None,
) -> dict:
    """
    Fetches records for a specific LAST_FIRST_NAME.

    NOTE:
    row_id is still used for cursor/keyset pagination.
    The employee lookup is performed using last_first_name.
    """

    if isinstance(filters, FiltersEnvelope):
        current_data = filters.filters
    else:
        current_data = filters or {}

    if isinstance(current_data, dict):
        current_data["last_first_name"] = FilterOps(eq=last_first_name)
    else:
        name_rule = FilterRule(
            field="last_first_name",
            ops=FilterOps(eq=last_first_name),
        )
        current_data.filters.append(name_rule)

    validated_filters = FiltersEnvelope(filters=current_data)

    current_page = page or PaginationModel(limit=50)
    current_sort = sort or SortModel()

    plan = _builder.get_list_plan(
        filters=validated_filters,
        sort=current_sort,
        page=current_page,
        columns=columns,
    )

    raw_results = execute_query(
        plan.sql,
        plan.params,
    )

    items = raw_results.get("items", [])

    return _format_paginated_response(
        items,
        current_page.limit,
    )
