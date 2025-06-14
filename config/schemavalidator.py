from typing import Any, Dict, List, Callable


class SchemaValidator:
    """
    Utility for validating configuration against schema definitions

    Provides methods for validating types and structures of configuration objects
    """

    # Type validators
    @staticmethod
    def is_int(value: Any) -> bool:
        return isinstance(value, int)

    @staticmethod
    def is_str(value: Any) -> bool:
        return isinstance(value, str)

    @staticmethod
    def is_bool(value: Any) -> bool:
        return isinstance(value, bool)

    @staticmethod
    def is_dict(value: Any) -> bool:
        return isinstance(value, dict)

    @staticmethod
    def is_list(value: Any) -> bool:
        return isinstance(value, list)

    @staticmethod
    def is_numeric_str(value: Any) -> bool:
        return isinstance(value, str) and value.isdigit()

    # Structure validators
    @staticmethod
    def validate_dict_with_types(
        value: Any,
        key_type_pairs: Dict[str, Callable[[Any], bool]],
        path: str = "",
        optional_keys: List[str] | None = None,
    ) -> List[str]:
        """
        Validate a dictionary against a schema of key-type pairs

        Args:
            value: The value to validate
            key_type_pairs: Dictionary mapping keys to type validation functions
            path: Current path in the configuration (for error messages)
            optional_keys: List of keys that are optional

        Returns:
            List[str]: List of validation errors, empty if valid
        """
        errors = []

        if not SchemaValidator.is_dict(value):
            errors.append(
                f"Expected dictionary at '{path}', got {type(value).__name__}"
            )
            return errors

        optional_keys = optional_keys or []

        for key in key_type_pairs:
            if key not in value and key not in optional_keys:
                errors.append(f"Missing required key '{key}' at '{path}'")

        for key, val in value.items():
            if key in key_type_pairs:
                validator = key_type_pairs[key]
                current_path = f"{path}.{key}" if path else key

                if callable(validator):
                    if not validator(val):
                        type_name = validator.__name__.replace("is_", "")
                        errors.append(
                            f"Expected {type_name} for '{current_path}', got {type(val).__name__}"
                        )
                elif isinstance(validator, dict):
                    if not SchemaValidator.is_dict(val):
                        errors.append(
                            f"Expected dictionary for '{current_path}', got {type(val).__name__}"
                        )
                    else:
                        nested_errors = SchemaValidator.validate_dict_with_types(
                            val, validator, current_path, optional_keys=optional_keys
                        )
                        errors.extend(nested_errors)
                elif (
                    isinstance(validator, tuple)
                    and len(validator) == 2
                    and callable(validator[0])
                ):
                    if not SchemaValidator.is_dict(val):
                        errors.append(
                            f"Expected dictionary for '{current_path}', got {type(val).__name__}"
                        )
                        continue

                    for k, v in val.items():
                        if not validator[0](k):
                            key_type = validator[0].__name__.replace("is_", "")
                            errors.append(
                                f"Expected {key_type} for key in '{current_path}', got {type(k).__name__}"
                            )
                        if not validator[1](v):
                            val_type = validator[1].__name__.replace("is_", "")
                            errors.append(
                                f"Expected {val_type} for value at '{current_path}.{k}', got {type(v).__name__}"
                            )

        return errors
