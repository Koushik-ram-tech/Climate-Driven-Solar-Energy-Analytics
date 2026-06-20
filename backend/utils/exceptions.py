"""
backend/utils/exceptions.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Custom exception hierarchy for the AI-Powered Residential Solar Investment
Advisor backend. These types let every layer of the application (data
loading, request validation, calculation) raise a specific, catchable
error instead of a generic or built-in Python exception.

This module defines exceptions only. It contains no business logic, no
validation logic, no file access, and no logging — those concerns belong
to the layers that raise and catch these exceptions (data/data_loader.py,
services/*, schemas/*), not to this module.

HIERARCHY
─────────
  SolarAdvisorError
  │
  ├── DataLoaderError
  ├── CityNotFoundError
  ├── CalculationError
  └── InvalidAdvisorInputError

  All four are independent siblings under a single root. None of them
  subclasses another sibling, so each can be caught precisely without
  accidentally also catching an unrelated failure mode.

DEPENDENCIES
────────────
  None. Pure exception-definitions module — no imports required.
  Explicitly NOT imported: fastapi, pydantic, logging, any file-access
  module, any backend/services/* or data/data_loader.py module.

USAGE
─────
  from utils.exceptions import (
      SolarAdvisorError,
      DataLoaderError,
      CityNotFoundError,
      CalculationError,
      InvalidAdvisorInputError,
  )

  # Catch any backend-originated error:
  try:
      ...
  except SolarAdvisorError:
      ...

  # Catch a specific failure mode:
  try:
      row = loader.get_sdsf_row(city)
  except CityNotFoundError:
      ...
"""

from __future__ import annotations


class SolarAdvisorError(Exception):
    """
    Base class for all custom exceptions raised by the Solar Investment
    Advisor backend.

    Catching this type catches any backend-originated failure (data
    loading, city lookup, calculation, or input validation) without also
    catching unrelated built-in exceptions that indicate a genuine bug
    (e.g. an unguarded ``KeyError`` or ``AttributeError``).

    Not raised directly — always raised as one of its subclasses below.
    """


class DataLoaderError(SolarAdvisorError):
    """
    Raised when the SDSF dataset (sdsf_city_dashboard.csv) or the
    Investment Advisor dataset (solar_investment_advisor_results.csv)
    cannot be loaded or fails schema validation.

    Examples
    --------
    - CSV file missing from disk.
    - CSV is malformed or unreadable (encoding, parse failure).
    - A required column is missing from the loaded DataFrame.
    - A categorical column contains a value outside its known set.

    This indicates a problem with the data layer itself, not with a
    particular request — it should generally be treated as fatal at
    application startup rather than recoverable per-request.
    """


class CityNotFoundError(SolarAdvisorError):
    """
    Raised when a city requested by the frontend does not exist in the
    SDSF dataset.

    Examples
    --------
    - City name typo (e.g. "Bengalooru" instead of "Bengaluru").
    - An unsupported city outside the 15 cities covered by the dataset.
    - A city slug that does not resolve to any known city name.

    Unlike DataLoaderError, this reflects a problem with a single
    request's input, not with the dataset itself.
    """


class CalculationError(SolarAdvisorError):
    """
    Raised when a calculation cannot be completed.

    Examples
    --------
    - Division by zero (e.g. a zero tariff or zero irradiance value
      reaching a formula that divides by it).
    - Invalid system sizing inputs (e.g. negative or non-finite values
      reaching recommend_system_sizes()).
    - An invalid tariff value that produces a nonsensical or undefined
      result.

    This is distinct from InvalidAdvisorInputError: it represents a
    failure that occurs while a formula is being evaluated, not a
    failure detected up front on raw user input.
    """


class InvalidAdvisorInputError(SolarAdvisorError):
    """
    Raised when advisor request values fail validation before any
    calculation begins.

    Examples
    --------
    - Negative budget.
    - Zero or negative roof area.
    - Invalid monthly bill amount (e.g. zero, negative, or non-numeric).

    This is distinct from CalculationError: it represents a problem
    detected on the raw input itself, before that input is ever passed
    into a calculation function.
    """
