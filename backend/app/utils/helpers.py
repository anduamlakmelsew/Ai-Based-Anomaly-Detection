from datetime import datetime


def serialize_model(obj):
    """
    Convert SQLAlchemy object to dictionary
    """

    data = {}

    for column in obj.__table__.columns:
        value = getattr(obj, column.name)

        if isinstance(value, datetime):
            value = value.isoformat()

        data[column.name] = value

    return data


def serialize_list(objects):
    """
    Convert list of models to JSON list
    """

    return [serialize_model(obj) for obj in objects]