#!/usr/bin/env python3
"""Fail closed when the service catalog is inconsistent."""

from service_manifest import ROOT, validation_errors


def main() -> None:
    errors = validation_errors(ROOT, check_registry=True)
    if errors:
        raise SystemExit("\n".join(errors))
    print("service catalog: valid")


if __name__ == "__main__":
    main()
