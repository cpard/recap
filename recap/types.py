from __future__ import annotations

import copy
from typing import Any


class RecapType:
    """Base class for all Recap types."""

    # Define and register built-in aliases
    type_registry: dict[str, RecapType] = {}

    def __init__(
        self,
        type_: str,
        logical: str | None = None,
        alias: str | None = None,
        doc: str | None = None,
        **extra_attrs,
    ):
        self.type_ = type_
        self.logical = logical
        self.alias = alias
        self.doc = doc
        self.extra_attrs = extra_attrs
        if alias is not None:
            if alias in RecapType.type_registry:
                raise ValueError(f"Alias {alias} is already used.")
            RecapType.type_registry[alias] = self

    @staticmethod
    def from_alias(alias: str) -> RecapType:
        try:
            return RecapType.type_registry[alias]
        except KeyError:
            raise TypeError(f"No RecapType with alias {alias} found.")

    def __eq__(self, other):
        if type(self) is type(other):
            return (
                self.type_,
                self.logical,
                self.alias,
                self.doc,
                self.extra_attrs,
            ) == (other.type_, other.logical, other.alias, other.doc, other.extra_attrs)
        return False


class NullType(RecapType):
    """Represents a null Recap type."""

    def __init__(self, **extra_attrs):
        super().__init__("null", **extra_attrs)


class BoolType(RecapType):
    """Represents a boolean Recap type."""

    def __init__(self, **extra_attrs):
        super().__init__("bool", **extra_attrs)


class IntType(RecapType):
    """Represents an integer Recap type."""

    def __init__(self, bits: int, signed: bool = True, **extra_attrs):
        super().__init__("int", **extra_attrs)
        self.bits = bits
        self.signed = signed

    def __eq__(self, other):
        return super().__eq__(other) and (self.bits, self.signed) == (
            other.bits,
            other.signed,
        )


class FloatType(RecapType):
    """Represents a floating point Recap type."""

    def __init__(self, bits: int, **extra_attrs):
        super().__init__("float", **extra_attrs)
        self.bits = bits

    def __eq__(self, other):
        return super().__eq__(other) and self.bits == other.bits


class StringType(RecapType):
    """Represents a string Recap type."""

    def __init__(self, bytes_: int, variable: bool = True, **extra_attrs):
        super().__init__("string", **extra_attrs)
        self.bytes_ = bytes_
        self.variable = variable

    def __eq__(self, other):
        return super().__eq__(other) and (self.bytes_, self.variable) == (
            other.bytes_,
            other.variable,
        )


class BytesType(RecapType):
    """Represents a bytes Recap type."""

    def __init__(self, bytes_: int, variable: bool = True, **extra_attrs):
        super().__init__("bytes", **extra_attrs)
        self.bytes_ = bytes_
        self.variable = variable

    def __eq__(self, other):
        return super().__eq__(other) and (self.bytes_, self.variable) == (
            other.bytes_,
            other.variable,
        )


class ListType(RecapType):
    """Represents a list Recap type."""

    def __init__(
        self,
        values: RecapType,
        length: int | None = None,
        variable: bool = True,
        **extra_attrs,
    ):
        super().__init__("list", **extra_attrs)
        self.values = values
        self.length = length
        self.variable = variable

    def __eq__(self, other):
        return super().__eq__(other) and (self.values, self.length, self.variable) == (
            other.values,
            other.length,
            other.variable,
        )


class MapType(RecapType):
    """Represents a map Recap type."""

    def __init__(self, keys: RecapType, values: RecapType, **extra_attrs):
        super().__init__("map", **extra_attrs)
        self.keys = keys
        self.values = values

    def __eq__(self, other):
        return super().__eq__(other) and (self.keys, self.values) == (
            other.keys,
            other.values,
        )


class StructType(RecapType):
    """Represents a struct Recap type."""

    def __init__(self, fields: list[RecapType] | None = None, **extra_attrs):
        super().__init__("struct", **extra_attrs)
        self.fields = fields if fields is not None else []

    def __eq__(self, other):
        return super().__eq__(other) and self.fields == other.fields


class EnumType(RecapType):
    """Represents an enum Recap type."""

    def __init__(self, symbols: list[str], **extra_attrs):
        super().__init__("enum", **extra_attrs)
        self.symbols = symbols

    def __eq__(self, other):
        return super().__eq__(other) and self.symbols == other.symbols


class UnionType(RecapType):
    """Represents a union Recap type."""

    def __init__(self, types: list[RecapType | str], **extra_attrs):
        super().__init__("union", **extra_attrs)
        self.types = types

    def __eq__(self, other):
        return super().__eq__(other) and self.types == other.types


class ProxyType(RecapType):
    """Represents a proxy to an aliased Recap type."""

    def __init__(self, alias: str, **extra_attrs):
        super().__init__("proxy", **extra_attrs)
        self.alias = alias
        self._resolved = None

    def resolve(self) -> RecapType:
        if self._resolved is None:
            self._resolved = copy.deepcopy(RecapType.from_alias(self.alias))
            # Apply attribute overrides
            for attr, value in self.extra_attrs.items():
                if hasattr(self._resolved, attr):
                    setattr(self._resolved, attr, value)
                else:
                    self._resolved.extra_attrs[attr] = value
        return self._resolved

    def __eq__(self, other):
        return super().__eq__(other) and self.alias == other.alias


# Built-in Aliases
RecapType.type_registry.update(
    {
        "int8": IntType(8, signed=True),
        "uint8": IntType(8, signed=False),
        "int16": IntType(16, signed=True),
        "uint16": IntType(16, signed=False),
        "int32": IntType(32, signed=True),
        "uint32": IntType(32, signed=False),
        "int64": IntType(64, signed=True),
        "uint64": IntType(64, signed=False),
        "float16": FloatType(16),
        "float32": FloatType(32),
        "float64": FloatType(64),
        "string32": StringType(bytes_=2_147_483_648, variable=True),
        "string64": StringType(bytes_=9_223_372_036_854_775_807, variable=True),
        "bytes32": BytesType(bytes_=2_147_483_648, variable=True),
        "bytes64": BytesType(bytes_=9_223_372_036_854_775_807, variable=True),
        "uuid": StringType(logical="build.recap.UUID", bytes_=36, variable=False),
        "decimal128": BytesType(
            logical="build.recap.Decimal",
            bytes_=16,
            variable=False,
            precision=28,
            scale=14,
        ),
        "decimal256": BytesType(
            logical="build.recap.Decimal",
            bytes_=32,
            variable=False,
            precision=56,
            scale=28,
        ),
        "duration64": IntType(
            logical="build.recap.Duration",
            bits=64,
            signed=True,
            unit="millisecond",
        ),
        "interval128": BytesType(
            logical="build.recap.Interval",
            bytes_=16,
            variable=False,
            unit="millisecond",
        ),
        "time32": IntType(
            logical="build.recap.Time",
            bits=32,
            signed=True,
            unit="second",
        ),
        "time64": IntType(
            logical="build.recap.Time",
            bits=64,
            signed=True,
            unit="second",
        ),
        "timestamp64": IntType(
            logical="build.recap.Timestamp",
            bits=64,
            signed=True,
            unit="millisecond",
            timezone="UTC",
        ),
        "date32": IntType(
            logical="build.recap.Date",
            bits=32,
            signed=True,
            unit="day",
        ),
        "date64": IntType(
            logical="build.recap.Date",
            bits=64,
            signed=True,
            unit="day",
        ),
    }
)


def from_dict(type_dict: dict[str, Any]) -> RecapType:
    type_dict = (
        type_dict.copy()
    )  # Create a copy to avoid modifying the input dictionary

    alias = type_dict.pop("alias", None)
    type_name = type_dict.pop("type", None)

    if type_name is None:
        raise ValueError(
            "'type' is a required field and was not found in the dictionary."
        )

    if isinstance(type_name, list):
        # If type is a list, handle as a union
        union_types = []
        for t in type_name:
            if isinstance(t, dict):
                union_types.append(from_dict(t))
            elif isinstance(t, str):
                union_types.append(from_dict({"type": t}))
        recap_type = UnionType(union_types, **type_dict)
    elif isinstance(type_name, str):
        match type_name:
            case "null":
                recap_type = NullType(**type_dict)
            case "bool":
                recap_type = BoolType(**type_dict)
            case "int":
                if "bits" not in type_dict:
                    raise ValueError("'bits' attribute is required for 'int' type.")
                recap_type = IntType(**type_dict)
            case "float":
                if "bits" not in type_dict:
                    raise ValueError("'bits' attribute is required for 'float' type.")
                recap_type = FloatType(**type_dict)
            case "string":
                if "bytes" not in type_dict:
                    raise ValueError("'bytes' attribute is required for 'string' type.")
                type_dict["bytes_"] = type_dict.pop("bytes")
                recap_type = StringType(**type_dict)
            case "bytes":
                if "bytes" not in type_dict:
                    raise ValueError("'bytes' attribute is required for 'bytes' type.")
                type_dict["bytes_"] = type_dict.pop("bytes")
                recap_type = BytesType(**type_dict)
            case "list":
                if "values" not in type_dict:
                    raise ValueError("'values' attribute is required for 'list' type.")
                recap_type = ListType(from_dict(type_dict.pop("values")), **type_dict)
            case "map":
                if "keys" not in type_dict or "values" not in type_dict:
                    raise ValueError(
                        "'keys' and 'values' attributes are required for 'map' type."
                    )
                recap_type = MapType(
                    from_dict(type_dict.pop("keys")),
                    from_dict(type_dict.pop("values")),
                    **type_dict,
                )
            case "struct":
                type_dict["fields"] = [
                    from_dict(f) for f in type_dict.get("fields", [])
                ]
                recap_type = StructType(**type_dict)
            case "enum":
                if "symbols" not in type_dict:
                    raise ValueError("'symbols' attribute is required for 'enum' type.")
                recap_type = EnumType(**type_dict)
            case "union":
                if "types" not in type_dict:
                    raise ValueError("'types' attribute is required for 'union' type.")
                recap_type = UnionType(
                    [from_dict(t) for t in type_dict.pop("types")], **type_dict
                )
            case _:
                recap_type = ProxyType(type_name, **type_dict)
    else:
        raise ValueError("'type' must be a string or list.")

    # If alias exists, register the created RecapType
    if alias:
        RecapType.type_registry[alias] = recap_type

    return recap_type
