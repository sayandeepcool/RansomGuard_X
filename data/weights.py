def calculate_sample_weight(label, style, mode):
    if label == 0:
        return 2.5 if style in ["zip_archive", "bulk_rename", "media_export"] else 1.0
    return 1.5
