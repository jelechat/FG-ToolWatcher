# .tools/database/utils/config_schema.py
import re
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BaseValidation(BaseModel):
    model_config = ConfigDict(extra="forbid")

class EanValidation(BaseValidation):
    type: Literal["ean"]

class MpnValidation(BaseValidation):
    type: Literal["mpn"]

class PriceValidation(BaseValidation):
    type: Literal["price"]

class TextValidation(BaseValidation):
    type: Literal["text"]

ValidationRule = Annotated[
    Union[EanValidation, MpnValidation, PriceValidation, TextValidation],
    Field(discriminator="type")
]

class FetchConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timeout: int = 15
    retries: int = 3
    impersonate: str = "chrome"

class FieldConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["identity", "price"]
    label: str | None = None
    required: bool = False
    sources: list[str | dict[str, str]] = Field(default_factory=list)
    vat_included: bool | None = None
    validate_rules: ValidationRule | None = Field(None, alias="validate")

    @field_validator("sources")
    @classmethod
    def check_sources_format(cls, sources):
        for s in sources:
            if isinstance(s, dict) and len(s) != 1:
                raise ValueError(f"Une source dict doit avoir exactement une clé. Reçu : {s}")
        return sources

class SiteConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    base_url: str
    enabled: bool = True
    currency: str = "EUR"
    vat_rate: float = 1.21  # Coefficient

    sitemaps: list[str] = Field(default_factory=list)
    product_url_patterns: list[re.Pattern] = Field(default_factory=list)
    exclude_url_patterns: list[re.Pattern] = Field(default_factory=list)

    scope: str | None = None
    fetch: FetchConfig = Field(default_factory=FetchConfig)
    fields: dict[str, FieldConfig] = Field(default_factory=dict)

    @model_validator(mode='after')
    def normalize_and_check(self) -> 'SiteConfig':
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        for field_name, config in self.fields.items():
            if field_name == "price" and config.role != "price":
                raise ValueError(f"Le champ 'price' doit avoir le role 'price', pas '{config.role}'")
            if field_name == "price" and config.vat_included is None:
                raise ValueError("Le champ 'price' doit préciser 'vat_included' (true ou false).")
        return self

class WebsiteConfigRoot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1]
    sites: dict[str, SiteConfig]
