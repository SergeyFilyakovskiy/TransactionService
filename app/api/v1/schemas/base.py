from pydantic import BaseModel, model_validator


class EntityModel(BaseModel):

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def unwrap_value_objects(cls, data):
        if isinstance(data, dict) or not hasattr(data, "__dict__"):
            return data

        return {
            name: getattr(getattr(data, name, None), "value", getattr(data, name, None))
            for name in cls.model_fields
        }
