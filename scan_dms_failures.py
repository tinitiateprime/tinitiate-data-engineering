"repo_search_function": "get_gl_details",
"repo_key_function": "get_gl_details_by_project_id",

"service_search_function": "search_gl_details",
"service_key_function": "get_gl_details_by_project",

"handler_search_function": "search_gl_details_v1",
"handler_key_function": "get_gl_details_v1",

"key_column": "proj_id",
"key_argument": "proj_id",
"handler_path_parameter": "proj_id",
"sample_key": "P-1001",

"search_requires_key": False,

"supports_search": True,
"supports_key_lookup": True,
"supports_handler_key_lookup": True,

"repo_search_parameters": [
    "filters",
    "sort",
    "page",
    "columns",
],

"repo_key_parameters": [
    "proj_id",
    "page",
    "sort",
    "columns",
],

"service_search_parameters": [
    "filters",
    "sort",
    "page",
    "columns",
],

"service_key_parameters": [
    "proj_id",
    "page",
    "sort",
    "columns",
],

"handler_service_parameters": [
    "filters",
    "sort",
    "page",
    "columns",
],
