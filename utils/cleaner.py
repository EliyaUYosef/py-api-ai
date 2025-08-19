# utils/cleaner.py
def clean_docai_json_for_file_request(data: dict) -> dict:
    data = data.copy()

    # מחיקת שדות כלליים
    data.pop("pages", None)
    data.pop("text_styles", None)

    if "entities" in data and isinstance(data["entities"], list):
        for entity in data["entities"]:
            # ניקוי text_anchor מה-entity
            if "text_anchor" in entity:
                entity["text_anchor"].pop("text_segments", None)
                entity["text_anchor"].pop("page_anchor", None)

            # מחיקת page_anchor מה-entity הראשי
            entity.pop("page_anchor", None)

            # ניקוי properties
            for prop in entity.get("properties", []):
                prop.pop("text_anchor", None)
                prop.pop("page_anchor", None)

    return data



def clean_docai_json_for_image_request(data: dict) -> dict:
    data = data.copy()

    data.pop("pages", None)
    data.pop("text_styles", None)

    if "entities" in data and isinstance(data["entities"], list):
        for entity in data["entities"]:
            if "text_anchor" in entity:
                entity["text_anchor"].pop("text_segments", None)
                entity["text_anchor"].pop("page_anchor", None)

    return data

