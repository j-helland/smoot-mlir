#pragma once

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Handle to a parsed Unit instance.
 */
typedef struct Units_Unit Units_Unit;

typedef struct Units_UnitResult {
  bool ok;
  Units_Unit *value;
  char *error;
} Units_UnitResult;

typedef struct Units_StringResult {
  bool ok;
  char *value;
  char *error;
} Units_StringResult;

/**
 * Parse a unit expression string e.g. `meter / second ** 2`.
 */
Units_UnitResult units_parse_unit(const char *expression);

/**
 * Format a unit instance into a string representation.
 *
 * Can round-trip through the parser.
 */
Units_StringResult units_format_unit(const Units_Unit *unit);

Units_UnitResult units_mul(const Units_Unit *lhs, const Units_Unit *rhs);

Units_UnitResult units_add(const Units_Unit *lhs, const Units_Unit *rhs);

void units_free_unit(Units_Unit *unit);

void units_free_string(char *ptr);

#ifdef __cplusplus
}
#endif
