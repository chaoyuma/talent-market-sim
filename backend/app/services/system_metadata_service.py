from app.repositories.system_metadata_repository import (
    list_all_table_names,
    get_table_level_metadata,
    get_field_level_metadata,
)


def build_table_metadata_payload(db, table_name: str):
    """
    组织单表元数据返回结构。
    """
    table_meta = get_table_level_metadata(db, table_name)
    field_meta_rows = get_field_level_metadata(db, table_name)

    return {
        "table_name": table_name,
        "table_info": None if table_meta is None else {
            "field_meaning": table_meta.field_meaning,
            "data_source": table_meta.data_source,
            "notes": table_meta.notes,
            "sort_order": table_meta.sort_order,
        },
        "fields": [
            {
                "field_name": row.field_name,
                "field_type": row.field_type,
                "is_nullable": row.is_nullable,
                "default_value": row.default_value,
                "field_meaning": row.field_meaning,
                "example_value": row.example_value,
                "data_source": row.data_source,
                "notes": row.notes,
                "sort_order": row.sort_order,
            }
            for row in field_meta_rows
        ],
    }


def build_metadata_index_payload(db):
    """
    返回所有已登记元数据的表名列表。
    """
    table_names = list_all_table_names(db)
    return {
        "tables": table_names,
        "count": len(table_names),
    }