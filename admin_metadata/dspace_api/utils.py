def parse_metadata(metadata_list):
    """Convierte una lista de metadatos en un diccionario más legible."""
    metadata_dict = {}
    for metadata in metadata_list:
        key = metadata.get("key")
        value = metadata.get("value")
        if key in metadata_dict:
            metadata_dict[key].append(value)
        else:
            metadata_dict[key] = [value]
    return metadata_dict
